"""
Start command handler.

Handles /start command - the entry point for new users.
"""

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from services.user_service import UserService


router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message, user_service: UserService) -> None:
    """
    Handle /start command.
    
    Args:
        message: Incoming message
        user_service: User service for database operations
    """
    # TODO: Register or get user
    # TODO: Send welcome message
    # TODO: Show main menu
    pass
