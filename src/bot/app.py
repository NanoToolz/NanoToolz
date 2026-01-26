# ============================================
# BOT APPLICATION SETUP
# ============================================
# Initialize and start the bot

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from src.config import settings
from src.bot.routers import setup_routers

async def start_bot():
    """Initialize and start the bot"""
    # Create bot instance with token
    bot = Bot(token=settings.BOT_TOKEN)
    
    # Create dispatcher with memory storage for FSM
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Register all routers
    setup_routers(dp)
    
    # Delete webhook and drop pending updates
    await bot.delete_webhook(drop_pending_updates=True)
    
    try:
        print("🤖 Bot is running...")
        # Start polling for messages
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
