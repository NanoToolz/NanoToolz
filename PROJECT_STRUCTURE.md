# NanoToolz - Telegram Bot Project Structure

## 📁 Project Structure

```
NanoToolz/
├── main.py                 # Application entry point
├── config.py              # Configuration and settings
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── Dockerfile            # Docker container configuration
├── docker-compose.yml    # Docker Compose setup
│
├── bot/                  # Bot core functionality
│   ├── __init__.py      # Bot initialization
│   └── factory.py       # Bot and dispatcher factory
│
├── db/                   # Database layer
│   ├── __init__.py      # Database package init
│   ├── connection.py    # MongoDB connection management
│   ├── base_repository.py  # Base repository class
│   └── repositories/    # Data repositories
│       ├── __init__.py
│       └── user_repository.py  # User data operations
│
├── handlers/            # Message handlers
│   ├── __init__.py     # Handlers package init
│   ├── commands/       # Command handlers (/start, /help, etc.)
│   │   ├── __init__.py
│   │   ├── start.py
│   │   └── help.py
│   ├── callbacks/      # Callback query handlers
│   │   ├── __init__.py
│   │   └── main_menu.py
│   └── errors/         # Error handlers
│       └── __init__.py
│
├── services/           # Business logic layer
│   ├── __init__.py
│   └── user_service.py  # User business logic
│
├── middleware/         # Middleware components
│   ├── __init__.py
│   ├── auth_middleware.py      # Authentication
│   ├── logging_middleware.py   # Logging
│   └── rate_limit_middleware.py  # Rate limiting
│
└── utils/              # Utility functions and helpers
    ├── __init__.py
    ├── keyboards.py        # Keyboard builders
    ├── text_formatter.py   # Text formatting utilities
    ├── logging_config.py   # Logging configuration
    └── validators.py       # Input validators
```

## 🚀 Technology Stack

- **Python**: 3.11+
- **Bot Framework**: aiogram v3
- **Database**: MongoDB Atlas
- **Async Driver**: Motor
- **Configuration**: Pydantic Settings

## 📦 Installation

1. Clone the repository:
```bash
git clone https://github.com/asimgraphicx/NanoToolz.git
cd NanoToolz
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your bot token and MongoDB URI
```

5. Run the bot:
```bash
python main.py
```

## 🐳 Docker Deployment

Using Docker Compose:
```bash
docker-compose up -d
```

Using Docker only:
```bash
docker build -t nanotoolz .
docker run --env-file .env nanotoolz
```

## 🏗️ Architecture Overview

### Layers

1. **Bot Layer** (`bot/`)
   - Bot initialization and configuration
   - Dispatcher setup
   - Lifecycle management

2. **Database Layer** (`db/`)
   - MongoDB connection management
   - Repository pattern implementation
   - Data access abstraction

3. **Handlers Layer** (`handlers/`)
   - Command handlers (user commands)
   - Callback handlers (button clicks)
   - Error handlers (exception handling)

4. **Services Layer** (`services/`)
   - Business logic implementation
   - Coordination between handlers and repositories
   - Data validation and processing

5. **Middleware Layer** (`middleware/`)
   - Authentication and authorization
   - Request logging
   - Rate limiting
   - User tracking

6. **Utils Layer** (`utils/`)
   - Keyboard builders
   - Text formatting
   - Validators
   - Logging configuration

### Design Principles

- **Separation of Concerns**: Each layer has a specific responsibility
- **Dependency Injection**: Services and repositories are injected where needed
- **Repository Pattern**: Database operations are abstracted through repositories
- **Async/Await**: Fully asynchronous for optimal performance
- **Type Hints**: All functions use Python type hints for better IDE support
- **Scalability**: Structure supports easy addition of new features

## 📝 Configuration

Environment variables (`.env`):
```env
BOT_TOKEN=your_bot_token_here
ADMIN_IDS=123456789,987654321
MONGODB_URI=mongodb+srv://...
MONGODB_DB_NAME=nanotoolz
DEBUG=False
LOG_LEVEL=INFO
```

## 🔒 Security

- Environment variables for sensitive data
- Non-root Docker user
- Input validation and sanitization
- Rate limiting middleware
- Admin authorization checks

## 📈 Scalability Features

- Modular architecture for easy feature addition
- Repository pattern for flexible data layer
- Middleware system for cross-cutting concerns
- Service layer for complex business logic
- Separated handlers for better organization

## 🛠️ Development

This is a placeholder structure. To implement business logic:

1. Fill in TODO comments in each module
2. Add specific handlers for your use case
3. Implement repository methods for data operations
4. Create services for business logic
5. Add middleware as needed

## 📄 License

See LICENSE file for details.

## 👥 Contributing

Contributions are welcome! Please follow the existing code structure and style.
