"""
Bot factory module.

Handles creation and configuration of bot and dispatcher instances.
"""

from typing import Optional

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import settings


async def setup_bot() -> tuple[Bot, Dispatcher]:
    """
    Set up bot and dispatcher with all necessary configurations.
    
    Returns:
        tuple[Bot, Dispatcher]: Configured bot and dispatcher instances
    """
    # TODO: Create bot instance
    # TODO: Create dispatcher with FSM storage
    # TODO: Register all middleware
    # TODO: Register all handlers
    # TODO: Set up database connections
    
    pass


async def shutdown_bot(bot: Bot, dp: Dispatcher) -> None:
    """
    Gracefully shutdown bot and dispatcher.
    
    Args:
        bot: Bot instance to shutdown
        dp: Dispatcher instance to shutdown
    """
    # TODO: Close database connections
    # TODO: Close bot session
    # TODO: Stop dispatcher
    
    pass
