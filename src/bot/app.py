from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from src.config import settings
from src.bot.routers import setup_routers
from src.bot.middleware.typing import TypingMiddleware

async def start_bot():
    """Initialize and start the bot"""
    bot = Bot(token=settings.BOT_TOKEN)
    
    # Storage for FSM (Wizard steps)
    storage = MemoryStorage()
    
    dp = Dispatcher(storage=storage)
    
    # Register Middleware
    dp.update.outer_middleware(TypingMiddleware())
    
    # Setup Routers
    setup_routers(dp)
    
    # Delete webhook/drop pending updates to prevent flooding on restart
    await bot.delete_webhook(drop_pending_updates=True)
    
    try:
        print("🤖 Bot is running with JSON Database & High-Level UX...")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()