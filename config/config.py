# config/config.py
from pathlib import Path
from config.secrets import *
# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / 'logs'
DATA_DIR = BASE_DIR / 'data'

# Create necessary directories
LOG_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

# Home Assistant Configuration
HA_CONFIG = {
    'url': f'http://{HA_HOST}:{HA_PORT}/api',
    'token': HA_TOKEN,
    'excluded_domains': [
        'input_boolean', 'input_text', 'input_number', 'input_select',
        'automation', 'script', 'device_tracker', 'persistent_notification',
        'person', 'sun', 'zone', 'zone_group', 'tts'
    ],
    'excluded_sensor_prefixes': [
        'sensor.sun_next_', 'sensor.sun_', 'sensor.date_',
        'sensor.time_', 'sensor.last_boot', 'sensor.last_update'
    ],
    'important_attributes': {
        'light': ['friendly_name', 'brightness', 'color_temp'],
        'climate': ['friendly_name', 'current_temperature', 'temperature', 
                   'hvac_action', 'hvac_modes', 'min_temp', 'max_temp'],
        'sensor': ['friendly_name', 'unit_of_measurement'],
        'cover': ['friendly_name', 'current_position'],
        'default': ['friendly_name']
    }
}

# MongoDB Configuration
MONGO_CONFIG = {
    'host': MONGO_HOST,
    'port': MONGO_PORT,
    'db_name': MONGO_DB_NAME,
    'username': MONGO_USERNAME,
    'password': MONGO_PASSWORD
}


# OpenAI Configuration
OPENAI_CONFIG = {
    'api_key': OPENAI_API_KEY,
    'model': AI_MODEL_NAME
}

# Logging Configuration
LOG_CONFIG = {
    'home_assistant': str(LOG_DIR / 'home_assistant.log'),
    'openai': str(LOG_DIR / 'openai.log'),
    'database': str(LOG_DIR / 'database.log'),
    'app': str(LOG_DIR / 'app.log'),
    'level': 'INFO',
    'format': '%(asctime)s - %(levelname)s - %(message)s',
    'date_format': '%Y-%m-%d %H:%M:%S'
}

# App Configuration
APP_CONFIG = {
    'conversation_history_file': str(DATA_DIR / 'conversation_history.json'),
    'max_history': 15,
    'default_user': 'furkan',
    'default_location': 'bedroom'
}