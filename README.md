# NanoToolz

🚀 **Nanotoolz** – Scalable Telegram Bot built with Python (aiogram v3) and MongoDB Atlas.

A clean, production-ready Telegram bot structure designed for long-term scalability and maintainability.

## ✨ Features

- 🏗️ **Clean Architecture**: Separated layers (core, db, handlers, services)
- 🚀 **Modern Stack**: Python 3.11+, aiogram v3, MongoDB Atlas (Motor)
- 📦 **Modular Design**: Easy to extend and maintain
- 🐳 **Docker Ready**: Containerized deployment with Docker Compose
- 🔒 **Security First**: Environment-based configuration, input validation
- 📊 **Scalable**: Repository pattern, middleware system, service layer

## 🚀 Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/asimgraphicx/NanoToolz.git
   cd NanoToolz
   ```

2. **Set up environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the bot**:
   ```bash
   python main.py
   ```

## 🐳 Docker Deployment

```bash
docker-compose up -d
```

## 📁 Project Structure

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for detailed documentation.

```
NanoToolz/
├── main.py              # Entry point
├── config.py            # Configuration
├── bot/                 # Bot core
├── db/                  # Database layer
├── handlers/            # Message handlers
├── services/            # Business logic
├── middleware/          # Middleware components
└── utils/               # Utilities
```

## 🛠️ Tech Stack

- **Python 3.11+**
- **aiogram v3** - Modern Telegram Bot framework
- **MongoDB Atlas** - Cloud database
- **Motor** - Async MongoDB driver
- **Pydantic** - Settings management

## 📝 Configuration

Required environment variables:
- `BOT_TOKEN` - Telegram bot token from @BotFather
- `MONGODB_URI` - MongoDB Atlas connection string
- `ADMIN_IDS` - Comma-separated admin user IDs

See `.env.example` for all options.

## 🏗️ Architecture

- **Bot Layer**: Bot initialization and lifecycle
- **Database Layer**: MongoDB operations with repository pattern
- **Handlers Layer**: Command, callback, and error handlers
- **Services Layer**: Business logic and validation
- **Middleware Layer**: Auth, logging, rate limiting
- **Utils Layer**: Helpers and utilities

## 📄 License

See [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please maintain the existing code structure and style.

---

Built with ❤️ for scalability and clean code
