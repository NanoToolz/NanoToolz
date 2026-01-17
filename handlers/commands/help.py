"""
Help command handler.

Handles /help command - provides information and support.
"""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message


router = Router(name="help")


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """
    Handle /help command.
    
    Args:
        message: Incoming message
    """
    # TODO: Send help message with available commands
    # TODO: Provide links to support/documentation
    pass
