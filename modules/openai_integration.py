# modules/openai_integration.py

import json
from openai import OpenAI, APIError, APIConnectionError, RateLimitError
from config.config import OPENAI_API_KEY, AI_MODEL_NAME
from modules.logger import openai_logger
from modules.home_assistant import process_api_call

try:
    client = OpenAI(api_key=OPENAI_API_KEY)
    openai_logger.info("OpenAI client initialized successfully")
except Exception as e:
    openai_logger.error(f"Failed to initialize OpenAI client: {str(e)}", exc_info=True)
    raise

def send_to_gpt(conversation_history, name, location, message, date):
    """Sends a message to GPT and receives a response."""
    try:
        prompt = f"""   User: {name}
                        Location: {location}
                        Message: "{message}"
                        Time: {date} """

        conversation_history.append({"role": "user", "content": prompt})

        openai_logger.info(f"User Request - Name: {name}, Location: {location}")
        openai_logger.info(f"User Message: {message}")
        
        chat_completion = client.chat.completions.create(
            messages=conversation_history,
            model=AI_MODEL_NAME,
            max_tokens=15000,
            temperature=0.7,
        )

        response = chat_completion.choices[0].message.content
        openai_logger.info(f"GPT Response received - Length: {len(response)} characters")
        openai_logger.info(f"GPT Response: {response}")
        
        if isinstance(response, dict):
            response = json.dumps(response)
            openai_logger.debug("Converted dictionary response to JSON string")
            
        conversation_history.append({"role": "assistant", "content": response})
        return response

    except APIError as e:
        openai_logger.error(f"OpenAI API error: {str(e)}")
        raise Exception(f"OpenAI API error: {str(e)}")
    except APIConnectionError as e:
        openai_logger.error(f"OpenAI connection error: {str(e)}")
        raise Exception("Failed to connect to OpenAI service")
    except RateLimitError as e:
        openai_logger.error(f"OpenAI rate limit exceeded: {str(e)}")
        raise Exception("Rate limit exceeded, please try again later")
    except Exception as e:
        openai_logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise Exception(f"Unexpected error occurred: {str(e)}")

def parse_and_execute(response):
    """Parses GPT's response and executes commands."""
    try:
        openai_logger.info("Starting response parsing")
        
        if isinstance(response, dict):
            parsed_response = response
            openai_logger.debug("Response is already a dictionary")
        else:
            try:
                parsed_response = json.loads(response)
                openai_logger.info("Successfully parsed JSON response")
            except json.JSONDecodeError as e:
                openai_logger.error(f"JSON parsing failed: {str(e)}")
                openai_logger.debug(f"Invalid JSON content: {response}")
                raise Exception("Invalid response format from GPT")
            
        if 'message' in parsed_response:
            message = parsed_response['message']
            print(f"\n{message}")
            openai_logger.info(f"Assistant Message: {message}")
            
        if api_calls := parsed_response.get('api_calls'):
            total_calls = len(api_calls)
            openai_logger.info(f"Found {total_calls} API calls to execute")
            print("\nExecuting commands...")
            
            for index, api_call in enumerate(api_calls, 1):
                openai_logger.info(f"API Call {index}/{total_calls}: {api_call}")
                try:
                    process_api_call(api_call)
                    openai_logger.info(f"API Call {index}/{total_calls} executed successfully")
                except Exception as e:
                    openai_logger.error(f"API Call {index}/{total_calls} failed: {str(e)}")
                    print(f"Error executing command {index}")

        return parsed_response

    except Exception as e:
        openai_logger.error(f"Parse and execute error: {str(e)}", exc_info=True)
        print(f"Error: {str(e)}")
        return None