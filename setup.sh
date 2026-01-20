#!/bin/bash
# Quick start script for NanoToolz bot

echo "🚀 NanoToolz Bot Setup"
echo "======================="

# Check Python
python --version || { echo "❌ Python not found"; exit 1; }

# Install requirements
echo "📦 Installing dependencies..."
pip install -r requirements.txt || { echo "❌ Failed to install"; exit 1; }

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your BOT_TOKEN!"
    echo "   Example: BOT_TOKEN=123456:ABC..."
    echo ""
    echo "Get your token from @BotFather on Telegram"
    exit 0
fi

# Check BOT_TOKEN
if grep -q "YOUR_BOT_TOKEN" .env; then
    echo "❌ BOT_TOKEN not configured in .env"
    echo "Please update .env with your token from @BotFather"
    exit 1
fi

echo "✅ Setup complete!"
echo ""
echo "To start the bot, run:"
echo "  python main.py"
echo ""
echo "To run admin dashboard, in another terminal run:"
echo "  uvicorn web.admin:app --reload"
echo ""
echo "Open Telegram and search for your bot to test!"
