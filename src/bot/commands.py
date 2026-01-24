from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeChat

from src.config import settings
from src.logger import logger

# Edit this file to change bot command lists.
USER_COMMANDS = [
    ("start", "Start the bot"),
    ("help", "Show help menu"),
    ("shop", "Browse store"),
    ("cart", "View your cart"),
    ("topup", "Top up credits"),
    ("profile", "View your profile"),
    ("support", "Get support"),
]

ADMIN_COMMANDS = [
    ("setwelcome", "Set welcome message"),
    ("setwelcomeimage", "Set welcome image"),
    ("clearwelcome", "Clear custom welcome message"),
    ("clearwelcomeimage", "Clear welcome image"),
]


def _build_commands(items: list[tuple[str, str]]) -> list[BotCommand]:
    return [BotCommand(command=cmd, description=desc) for cmd, desc in items]


async def set_bot_commands(bot: Bot) -> None:
    """Set bot commands"""
    await bot.set_my_commands(_build_commands(USER_COMMANDS))

    if not settings.ADMIN_IDS:
        return

    admin_commands = _build_commands(USER_COMMANDS + ADMIN_COMMANDS)
    for admin_id in settings.ADMIN_IDS:
        try:
            await bot.set_my_commands(
                admin_commands,
                scope=BotCommandScopeChat(chat_id=admin_id),
            )
        except Exception as exc:
            logger.warning("Failed to set admin commands for %s: %s", admin_id, exc)
