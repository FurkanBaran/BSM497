# AI-Powered Smart Home Assistant

An intelligent home automation system that integrates OpenAI's GPT models with Home Assistant to provide natural language control of smart home devices and comprehensive household management.

## 🎯 Technical Highlights

- **AI Service Integration**: Production-ready integration of OpenAI GPT API with structured prompt engineering and response parsing
- **Backend Development**: Python-based modular architecture with API client implementation and service orchestration
- **Database Management**: MongoDB integration with automated data pipelines and 20+ CRUD operations
- **Containerization**: Docker-based deployment with multi-service orchestration
- **Production Features**: Comprehensive error handling, automatic retry mechanisms, and multi-stream logging system

## 🌟 Features

### Smart Home Control
- **Natural Language Processing**: Control your smart home devices using conversational language
- **Home Assistant Integration**: Full integration with Home Assistant API for device control
- **Real-time State Monitoring**: Continuously monitors and reports on the state of all connected devices
- **Multi-domain Support**: Controls lights, climate systems, sensors, covers, and more

### Household Management
- **User Management**: Track family members with health records and status monitoring
- **Inventory System**: Manage household items with quantity tracking and low-stock alerts
- **Shopping List**: Dynamic shopping list with status tracking (pending/bought)
- **Task Management**: Create, assign, and track tasks with due dates and priorities
- **Daily Activity Logging**: Automatic logging of important household events and activities

### AI Intelligence
- **Context-Aware Responses**: Maintains conversation history for contextual understanding
- **Proactive Logging**: Automatically logs important daily events without explicit requests
- **Multi-language Support**: Responds in the user's language
- **Smart Reminders**: Provides departure reminders with pending tasks and shopping items

## 🏗️ Architecture

### System Design

The application follows a modular architecture with clear separation of concerns:

- **AI Integration Layer**: OpenAI GPT API integration with custom prompt engineering and structured JSON response parsing
- **API Client Layer**: HTTP client for Home Assistant REST API with Bearer token authentication
- **Data Management Layer**: MongoDB operations with schema validation and automated data pipelines
- **Application Layer**: Main orchestrator handling conversation flow, retry logic, and error management

### Project Structure

```
BSM497-master/
├── config/
│   ├── config.py         # Configuration management
│   └── secrets.py        # API keys and credentials
├── modules/
│   ├── conversation_history.py    # Chat history and system prompts
│   ├── home_assistant.py         # Home Assistant API integration
│   ├── openai_integration.py     # OpenAI GPT integration
│   ├── logger.py                 # Logging system
│   ├── utils.py                  # Utility functions
│   └── data/
│       ├── DatabaseManager.py    # MongoDB operations
│       └── DatabaseSetup.py      # Database initialization
├── main.py               # Application entry point
├── docker-compose.yml    # Docker services configuration
└── requirements.txt      # Python dependencies
```

### Technology Stack

- **AI/LLM**: OpenAI GPT-4o-mini API with conversation context management
- **Backend**: Python 3.8+ with modular design
- **Database**: MongoDB with schema validation and indexing
- **API Client**: HTTP client for Home Assistant REST API integration
- **Deployment**: Docker Compose for multi-container orchestration
- **Logging**: Rotating file handlers with separate streams for each component

## 📋 Prerequisites

- Python 3.8+
- MongoDB (local or Docker)
- Home Assistant instance
- OpenAI API key
- Docker and Docker Compose (optional)

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd BSM497-master
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Credentials

Edit `config/secrets.py` with your credentials:

```python
# Home Assistant
HA_HOST = 'localhost'
HA_PORT = 8123
HA_TOKEN = "your_home_assistant_token"

# MongoDB
MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_DB_NAME = 'home_assistant'
MONGO_USERNAME = 'your_username'
MONGO_PASSWORD = 'your_password'

# OpenAI
OPENAI_API_KEY = "your_openai_api_key"
AI_MODEL_NAME = "gpt-4o-mini"  # or "gpt-4"
```

### 4. Start Services with Docker (Recommended)

```bash
docker-compose up -d
```

This will start:
- MongoDB on port 27017
- Home Assistant on port 8123

### 5. Run the Application

```bash
python main.py
```

## 🐳 Deployment

The application uses Docker Compose for multi-container orchestration:

**Services:**
- **MongoDB**: NoSQL database with persistent volume
- **Home Assistant**: IoT platform for device control

**Deployment Features:**
- Health checks for service availability
- Persistent data storage with named volumes
- Network isolation and service dependencies
- Environment-based configuration
- Timezone configuration (Europe/Istanbul)

**Production Considerations:**
- Use environment variables for sensitive data
- Implement MongoDB authentication in production
- Configure HTTPS for external access
- Set up log aggregation for monitoring

## 📖 Usage

### Context-Aware Interaction

The system understands context and user location to provide intelligent responses:

```
Your message: Turn on the lights
Assistant: I've turned on the bedroom lights for you.
(System knows user is in bedroom from location context)

Your message: I used all the tomatoes, cooking pasta now
Assistant: Noted! I've added tomatoes to your shopping list and logged that you're cooking pasta for dinner.
(System automatically infers shopping list update and logs daily activity)

Your message: I'm leaving home now
Assistant: Have a safe trip! Quick reminder: you have 2 pending tasks - 
"Take out trash" due today, and don't forget to buy milk and tomatoes. 
The living room lights are still on, should I turn them off?
(System checks tasks, shopping list, and device states proactively)

Your message: It's too cold in here
Assistant: I've set the bedroom temperature to 24 degrees. Current temperature is 20 degrees, it should warm up shortly.
(System knows user location and adjusts the right climate device)
```

### Database Operations

The system automatically manages database operations based on context:

- **User Management**: Add family members, track health status
- **Inventory**: Track household items and quantities
- **Tasks**: Create and manage household tasks
- **Daily Logs**: Automatic logging of daily activities

### Automatic Logging

The system automatically logs:
- Home arrivals and departures
- Meal preparations
- Health-related events
- Important conversations
- System changes

## 🔧 Configuration

### Home Assistant Configuration

Edit `config/config.py` to customize:

```python
HA_CONFIG = {
    'excluded_domains': ['automation', 'script', ...],
    'excluded_sensor_prefixes': ['sensor.sun_', ...],
    'important_attributes': {
        'light': ['friendly_name', 'brightness', 'color_temp'],
        ...
    }
}
```

### OpenAI Configuration

```python
OPENAI_CONFIG = {
    'api_key': OPENAI_API_KEY,
    'model': AI_MODEL_NAME  # gpt-4o-mini, gpt-4, etc.
}
```

### Logging Configuration

```python
LOG_CONFIG = {
    'level': 'INFO',  # DEBUG, INFO, WARNING, ERROR
    'format': '%(asctime)s - %(levelname)s - %(message)s',
}
```

## 🗄️ Database Schema

### Collections

1. **users**: Family member information and health records
2. **inventory**: Household items with quantities and categories
3. **shopping_list**: Shopping items with status tracking
4. **tasks**: Task management with assignments and due dates
5. **daily_log**: Daily activity logs with timestamps

## 🔍 API Integration Details

### Home Assistant API

The system interacts with Home Assistant through REST API with Bearer token authentication:

- `GET /api/states` - Fetch device states
- `GET /api/services` - Get available services
- `POST /api/services/{domain}/{service}` - Execute commands

### OpenAI API

Uses OpenAI's Chat Completions API with custom prompt engineering:

- Maintains conversation history for context (15-message window)
- Dynamic system prompts with real-time state injection
- Structured JSON responses for reliable parsing
- Temperature: 0.7 for balanced creativity
- Custom response format with action mapping (API calls + DB operations)

## 📊 Response Format

The AI assistant responds in structured JSON:

```json
{
  "message": "User-friendly response text",
  "api_calls": [
    {
      "action": "light.turn_on",
      "entity_id": "light.living_room",
      "parameters": {"brightness": 255}
    }
  ],
  "db_calls": [
    {
      "function": "add_daily_log",
      "parameters": {
        "title": "Event Title",
        "details": "Event description"
      }
    }
  ],
  "need_response": false
}
```

## 🛠️ Database Operations

The system implements a comprehensive data management layer with automated pipelines for logging, inventory tracking, and task management. All operations include error handling and are accessible through natural language commands via the AI assistant.

### Available Functions

**User Operations:**
- `add_user(name, role, age=None)`
- `get_user(name)`
- `get_all_users()`
- `update_user_health(name, status=None, medical_record=None)`
- `get_user_health(name)`

**Inventory Operations:**
- `add_inventory_item(name, category, quantity, info=None)`
- `get_inventory_item(name)`
- `update_inventory_quantity(name, new_quantity)`
- `get_low_stock_items()`

**Shopping List Operations:**
- `add_to_shopping_list(item_data)`
- `get_shopping_list()`
- `update_shopping_item_status(name, new_status)`
- `get_pending_shopping_items()`

**Task Operations:**
- `add_task(name, assigned_to=None, due_date=None, info=None)`
- `complete_task(name)`
- `get_pending_tasks()`
- `get_overdue_tasks()`

**Daily Log Operations:**
- `add_daily_log(title, details=None)`
- `get_today_logs()`
- `get_date_logs(date)`

## 📝 Logging

The system maintains separate log files for different components:

- `logs/app.log` - Main application logs
- `logs/home_assistant.log` - Home Assistant integration logs
- `logs/openai.log` - OpenAI API interaction logs
- `logs/database.log` - Database operation logs

Logs include:
- Timestamps
- Log levels (INFO, WARNING, ERROR)
- Detailed error messages and stack traces

## 🔒 Security Considerations

1. **API Keys**: Store sensitive credentials in `secrets.py` (not in version control)
2. **MongoDB**: Use authentication in production environments
3. **Home Assistant Token**: Use long-lived access tokens with appropriate permissions
4. **Network**: Consider using HTTPS for Home Assistant API calls

## 🐛 Troubleshooting

### Common Issues

**Connection to Home Assistant fails:**
- Verify HA_HOST and HA_PORT in secrets.py
- Check Home Assistant is running and accessible
- Validate the access token

**MongoDB connection error:**
- Ensure MongoDB is running (check with `docker ps`)
- Verify MongoDB credentials
- Check port 27017 is not blocked

**OpenAI API errors:**
- Verify API key is valid
- Check API rate limits
- Ensure sufficient API credits

**Invalid JSON response:**
- The system will automatically retry (up to 2 times)
- Check OpenAI logs for response content
- Consider adjusting temperature parameter

## 🚀 Advanced Features

### AI Orchestration Pipeline

The system implements a multi-stage AI pipeline:
1. **Prompt Engineering**: Dynamic system prompts with real-time device state injection
2. **Intent Processing**: Natural language understanding with structured JSON output
3. **Action Execution**: Orchestrated API calls to Home Assistant and database operations
4. **Response Generation**: Context-aware replies with automatic logging

### Conversation History Management

The system maintains conversation context:
- Keeps last 15 messages for context
- Refreshes system prompt with current home state
- Saves history to JSON file

### Smart Context Updates

System prompt includes:
- Current state of all devices
- Available services and entities
- Database operation context
- Response formatting rules

### Production-Ready Features

**Error Handling & Resilience:**
- Comprehensive try-catch blocks across all modules
- Automatic retry mechanism (up to 2 retries for failed requests)
- Graceful degradation on service failures
- Detailed error logging with stack traces

**Monitoring & Observability:**
- Multi-stream logging (4 separate log files)
- Rotating file handlers (100MB per file, 5 backups)
- Request/response logging for debugging
- Performance metrics tracking

**Security:**
- Environment-based secrets management
- Bearer token authentication for API calls
- Separation of configuration and credentials
- Input validation and sanitization

## 🤝 Contributing

Contributions are welcome! Please ensure:
- Code follows existing style patterns
- All functions include docstrings
- Error handling is comprehensive
- Logging is implemented appropriately


---

**Note**: This project requires active subscriptions/access to OpenAI API and a running Home Assistant instance. Ensure all prerequisites are met before deployment.

