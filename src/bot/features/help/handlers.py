from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from .messages import HELP_MESSAGE
from src.logger import logger
from src.middleware.rate_limiter import check_rate_limit

router = Router()


@router.message(Command("help"))
async def help_command(message: Message) -> None:
    """Handle /help command"""
    allowed, warn = check_rate_limit(message.from_user.id, with_warning=True)
    if not allowed:
        await message.answer("⏱️ Too many requests. Wait 30 seconds.")
        return
    if warn:
        await message.answer("⚠️ You're sending too many requests. Slow down.")
    try:
        await message.answer(HELP_MESSAGE, parse_mode="HTML")
    except Exception as exc:
        logger.error("Error in help_command: %s", exc)
        await message.answer("❌ Something went wrong. Try again.")


@router.callback_query(F.data == "help")
async def help_callback(query: CallbackQuery) -> None:
    allowed, warn = check_rate_limit(query.from_user.id, with_warning=True)
    if not allowed:
        await query.answer("⏱️ Too many requests. Wait 30 seconds.", show_alert=True)
        return
    if warn:
        await query.answer("⚠️ You're sending too many requests. Slow down.", show_alert=True)
    try:
        await query.message.edit_text(HELP_MESSAGE, parse_mode="HTML")
        await query.answer()
    except Exception as exc:
        logger.error("Error in help_callback: %s", exc)
        await query.answer("❌ Something went wrong. Try again.", show_alert=True)
