import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from src.config import settings
from src.bot.handlers import router

logger = logging.getLogger(__name__)

async def set_bot_commands(bot: Bot):
    """Set bot commands"""
    commands = [
        ("start", "Start the bot"),
        ("help", "Show help menu"),
        ("shop", "Browse store"),
        ("profile", "View your profile"),
        ("support", "Get support"),
    ]
    from aiogram.types import BotCommand
    await bot.set_my_commands([BotCommand(command=cmd, description=desc) for cmd, desc in commands])

def create_dispatcher():
    """Create dispatcher with handlers"""
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Include router
    dp.include_router(router)
    
    return dp
