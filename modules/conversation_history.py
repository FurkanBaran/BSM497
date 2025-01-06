# modules/conversation_history.py
import json
from config.config import DATA_DIR
from modules.home_assistant import get_ha_states
from modules.logger import openai_logger
from datetime import date

def format_home_structure(data):
    """Formats Home Assistant data in a concise yet complete manner."""
    if not data:
        return "Error: Could not fetch home state"

    context = "Home State:\n"
    
    entities_by_domain = {}
    for entity in data["entities"]:
        domain = entity["domain"]
        if domain not in entities_by_domain:
            entities_by_domain[domain] = []
        entities_by_domain[domain].append(entity)

    for domain, entities in sorted(entities_by_domain.items()):
        context += f"\n{domain}:\n"
        for entity in entities:
            # Main state information
            context += f"- {entity['entity_id']}: {entity['state']}"
            
            # Important attributes specific to the domain
            attrs = entity['attributes']
            if domain == 'climate':
                curr_temp = attrs.get('current_temperature')
                target_temp = attrs.get('temperature')
                if curr_temp or target_temp:
                    temps = []
                    if curr_temp: temps.append(f"current={curr_temp}°C")
                    if target_temp: temps.append(f"target={target_temp}°C")
                    context += f" ({', '.join(temps)})"
            elif domain == 'light' and 'brightness' in attrs:
                context += f" (brightness={attrs['brightness']})"
            elif domain == 'cover' and 'current_position' in attrs:
                context += f" (position={attrs['current_position']})"
            
            context += "\n"

    # Available services
    if data.get("services"):
        context += "\nAvailable Services:\n"
        for domain, services in sorted(data["services"].items()):
            context += f"{domain}: {', '.join(services)}\n"

    return context


    
def get_system_prompt():
    """Retrieves the current system prompt."""
    try:
        states = get_ha_states()
        home_state = format_home_structure(states) if states else "Error: Could not fetch home state"
        db_context= f"""
            USER:
            - add_user(name, role, age=None)  
                # Example: add_user("John", "father", 35)

            - get_user(name)  
                # Example: get_user("John")

            - get_all_users() 

            - update_user_health(name, status=None, medical_record=None)  
                # Example: update_user_health("John", "sick", 
                #          {{"type": "cold", "symptoms": "fever"}})

            - get_user_health(name)
                # Example: get_user_health("John")

            INVENTORY:
            - add_inventory_item(name, category, quantity, info=None)  
                # Example: add_inventory_item("milk", "food", 2, 
                #          {{"price": 3.99, "brand": "X"}})

            - get_inventory_item(name)
                # Example: get_inventory_item("milk")

            - update_inventory_quantity(name, new_quantity)
                # Example: update_inventory_quantity("milk", 3)

            - get_low_stock_items()

            SHOPPING LIST:
           - add_to_shopping_list(item_data)
                # Example: add_to_shopping_list({{
                    "item_data": {{
                        "name": "milk",
                        "status": "pending",
                        "info": {{"urgent": True}}
                    }}
                }})

            - get_shopping_list()
            - update_shopping_item_status(name, new_status)  # pending/bought
            - get_pending_shopping_items()

            TASKS:
            - add_task(name, assigned_to=None, due_date=None, info=None)
                # Example: add_task("Clean room", "John", "2024-01-10 15:00",
                #          {{"priority": "high"}})

            - complete_task(name)
            - get_pending_tasks()
            - get_overdue_tasks()

            DAILY LOG:
            - add_daily_log(title, details=None)
                # Example: add_daily_log("Family Dinner", "Had pizza together")

            - get_today_logs()
            - get_date_logs(date)  # Example: get_date_logs("2024-01-10")
            Note: All functions are flexible with minimal required fields

            **IMPORTANT**
            Even if not explicitly asked, log important daily life events and user health changes for future reference.

            LOGGING RULES:
            **ALWAYS** Log important daily life events:
            - Home entries/exits
            - Meals (cooking/eating desicions)
            - Activities (movies, games)
            - Health related
            - Important conversations
            - System changes

            Skip logging:
            - Greetings
            - Status checks
            - Simple queries


            EXIT RULES:
            When user indicates departure (leaving, goodbye, etc.):
            1. Create daily log (add_daily_log)
            2. Check pending tasks (get_pending_tasks)
            3. Check shopping list (get_pending_shopping_items)
            4. Combine all important reminders in a single message


            """
        return f"""You are an AI assistant for a smart home system.
 
CURRENT HOME STATE (Home Assistant):
{home_state}
 
DATABASE CONTEXT:
{db_context}

RESPONSE FORMAT:
{{
    "message": "Natural speech response for text-to-speech. Don't use special characters,symbols, or emojis.",
    "api_calls": [{{
        "action": "domain.service",
        "entity_id": "domain.entity_id",
        "parameters": {{}}
    }}] or null,
    "db_calls": [{{
        "function": "function_name",
        "parameters": {{}}
    }}] or null,
    "need_response": boolean  // Set true when making read operations and waiting for results
}}

RULES:
1. Only respond with JSON 
2. Use natural speech in the "message" field for text-to-speech. 
3. For Home Assistant:
   - Use ONLY services and entity_ids from CURRENT HOME STATE
   - Include appropriate parameters for each service
   - Ask for alarm code when needed
4. For Database Operations:
   - First make read operations if needed, NEVER assume database content - ALWAYS query first
   - Wait for results before making updates (set need_response: true)
   - Use exact function names as listed above
5. When need_response is true:
   - Wait for system to provide requested data
   - Generate new response based on received data

Note: After midnight, always check both current day and previous day logs to provide complete information about "today's" events, as users may refer to their daily cycle rather than calendar day.


Example Dialog:
User: "Hi I am at home, I'll cook chicken and rice for dinner. How's everything at home?"
Assistant: {{
    "message": "Welcome back! The living room temperature is twenty two degrees with lights on, bedroom at (...). Now checking today's events...",
    "db_calls": [{{
        "function": "add_daily_log",
        "parameters": {{
            "title": "Home Arrival",
            "details": "User arrived home and plans to cook chicken and rice for dinner"
        }}
    }}, {{
        "function": "get_today_logs",
        "parameters": {{}}
    }}, {{
        "function": "get_date_logs",
        "parameters": {{
            "date": "2025-01-04"
        }}
    }}],
    "need_response": true
}}

NOTE: Always answer in language of the user. Always use the same language as the user.

"""

    except Exception as e:
        openai_logger.error(f"Error getting system prompt: {e}")
        return None

def maintain_conversation_history():
    """Initializes the conversation history with the system prompt."""
    system_prompt = get_system_prompt()
    if system_prompt:
        return [{"role": "system", "content": system_prompt}]
    else:
        return [{"role": "system", "content": "Error initializing system prompt"}]

def refresh_system_prompt(conversation_history):
    """Updates the system prompt."""
    new_prompt = get_system_prompt()
    if new_prompt and conversation_history:
        conversation_history[0] = {"role": "system", "content": new_prompt}
    return conversation_history

def save_conversation_history(conversation_history, filename=DATA_DIR / 'conversation_history.json'):
    """Saves the conversation history to a file."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(conversation_history, f, ensure_ascii=False, indent=2)

def load_conversation_history(filename=DATA_DIR / 'conversation_history.json'):
    """Loads the conversation history from a file or initializes a new one."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                return maintain_conversation_history()
            try:
                history = json.loads(content)
                if not history or not isinstance(history, list):
                    return maintain_conversation_history()
                return history
            except json.JSONDecodeError:
                openai_logger.error("Error decoding conversation history JSON")
                return maintain_conversation_history()
    except FileNotFoundError:
        openai_logger.error("Conversation history file not found")
        return maintain_conversation_history()
