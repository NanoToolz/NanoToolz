from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from .messages import HELP_MESSAGE

router = Router()


@router.message(Command("help"))
async def help_command(message: Message) -> None:
    """Handle /help command"""
    await message.answer(HELP_MESSAGE, parse_mode="HTML")
