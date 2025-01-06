# main.py

import datetime
import json
from modules.home_assistant import process_api_call
from modules.openai_integration import send_to_gpt
from modules.conversation_history import (
    load_conversation_history,
    refresh_system_prompt,
    save_conversation_history
)
from modules.data.DatabaseManager import DatabaseManager  
from modules.data.DatabaseSetup import DatabaseSetup
from modules.logger import app_logger

class MainClass:
    def __init__(self):
        self.db = DatabaseManager()
        self.conversation_history = load_conversation_history()
        self.default_name = "Ali"
        self.default_location = "Living Room"
        app_logger.info("MainClass initialized")
    def process_db_calls(self, db_calls):
        results = []
        app_logger.info(f"Processing database calls: {db_calls}")
        
        if not isinstance(db_calls, list):
            app_logger.error("Invalid db_calls format: not a list")
            return [{'error': 'Invalid format'}]

        for call in db_calls:
            try:
                if not isinstance(call, dict) or 'function' not in call or 'parameters' not in call:
                    raise ValueError("Invalid call format")

                function_name = call['function']
                params = call['parameters']
                
                if not hasattr(self.db, function_name):
                    raise AttributeError(f"Function {function_name} not found")

                func = getattr(self.db, function_name)
                result = func(**params)
                results.append({
                    'function': function_name,
                    'result': result
                })
                app_logger.info(f"Successfully executed DB call: {function_name}")
                
            except Exception as e:
                error_msg = f"Error in {function_name}: {str(e)}"
                app_logger.error(error_msg)
                results.append({
                    'function': function_name,
                    'error': error_msg
                })
                
        return results

    def process_response(self, response):
        return_message = ""
        if not response:
            app_logger.warning("Empty response received")
            return None
            
        try:
            parsed_response = json.loads(response)
            app_logger.info(f"Successfully parsed response: {parsed_response}")
        except json.JSONDecodeError as e:
            app_logger.error(f"Invalid JSON response: {e}")
            return "Your last response was not valid JSON. Please provide a properly formatted response."
        
        try:
            # Message handling
            if message := parsed_response.get('message'):
                app_logger.info(f"Processing assistant message: {message}")
                print("Assistant:", message)

            # API calls
            if api_calls := parsed_response.get('api_calls'):
                app_logger.info(f"Processing API calls: {api_calls}")
                for api_call in api_calls:
                    try:
                        process_api_call(api_call)
                        app_logger.info(f"Successfully executed API call: {api_call}")
                        return_message += f"API call result: {api_call}"
                    except Exception as e:
                        app_logger.error(f"API call error: {e}")
                        return_message += f"API call error: {e}"

            # Database calls
            if db_calls := parsed_response.get('db_calls'):
                try:
                    db_results = self.process_db_calls(db_calls)
                    if parsed_response.get('need_response'):
                        app_logger.info(f"Database operation results: {db_results}")
                        return_message += f"Database operation results: {db_results}"
                except Exception as e:
                    app_logger.error(f"Database operation failed: {e}")
                    return_message += f"Database operation failed: {e}, please try again."

            return None if not parsed_response.get('need_response') else (return_message or None)

        except Exception as e:
            app_logger.error(f"Response processing error: {e}")
            return None

    def main_loop(self):
        try:
            app_logger.info("Starting database setup...")
            DatabaseSetup().setup()
            app_logger.info("Database setup completed")
            
            while True:
                try:
                    self.conversation_history = refresh_system_prompt(self.conversation_history)
                    
                    message = input("Your message: ").strip()
                    if not message:
                        continue
                        
                    if message.lower() in ['quit', 'exit', 'bye']:
                        app_logger.info("User requested exit")
                        print("Goodbye!")
                        break

                    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M %A")
                    app_logger.info(f"Processing user message: '{message}' at {date}")

                    retry_count = 0
                    while retry_count < 2:  # Max 2 retries
                        app_logger.info(f"Attempt {retry_count + 1} to process message")
                        response = send_to_gpt(
                            self.conversation_history, 
                            self.default_name,
                            self.default_location, 
                            message, 
                            date
                        )
                        
                        if not response:
                            app_logger.warning("No response received from GPT")
                            break

                        next_message = self.process_response(response)
                        
                        if next_message is None:
                            app_logger.info("Processing completed")
                            break
                        elif next_message and "not valid JSON" in next_message:
                            app_logger.warning(f"Invalid JSON response, attempt {retry_count + 1}")
                            retry_count += 1
                            message = next_message
                            continue
                        elif next_message:
                            app_logger.info(f"Continuing with new message: {next_message}")
                            message = next_message
                            continue
                        break

                    # Conversation history management
                    if len(self.conversation_history) > 15:
                        app_logger.info("Trimming conversation history")
                        self.conversation_history = [
                            self.conversation_history[0]
                        ] + self.conversation_history[-14:]
                    
                    save_conversation_history(self.conversation_history)
                    app_logger.info("Conversation history saved")

                except Exception as e:
                    app_logger.error(f"Loop iteration error: {e}")
                    print("An error occurred. Continuing with next input...")

        except KeyboardInterrupt:
            app_logger.info("Program terminated by user (KeyboardInterrupt)")
            print("\nProgram terminated by user.")
        except Exception as e:
            app_logger.error(f"Fatal error occurred: {e}")
            print("A fatal error occurred. Please check the logs.")
        finally:
            app_logger.info("Closing database connection and saving conversation history")
            self.db.close()
            save_conversation_history(self.conversation_history)

if __name__ == "__main__":
    app_logger.info("Starting application")
    MainClass().main_loop()