"""
Bot package initialization.

This package contains the core bot functionality including
bot creation, dispatcher setup, and bot lifecycle management.
"""

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import settings


def create_bot() -> Bot:
    """
    Create and configure the bot instance.
    
    Returns:
        Bot: Configured aiogram Bot instance
    """
    # TODO: Initialize bot with token from settings
    # TODO: Configure default properties (parse mode, etc.)
    pass


def create_dispatcher() -> Dispatcher:
    """
    Create and configure the dispatcher.
    
    Returns:
        Dispatcher: Configured aiogram Dispatcher instance
    """
    # TODO: Initialize dispatcher
    # TODO: Register middleware
    # TODO: Register handlers
    pass


__all__ = ["create_bot", "create_dispatcher"]
