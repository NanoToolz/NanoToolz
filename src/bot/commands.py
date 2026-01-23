from aiogram import Bot
from aiogram.types import BotCommand

COMMANDS = [
    ("start", "Start the bot"),
    ("help", "Show help menu"),
    ("shop", "Browse store"),
    ("cart", "View your cart"),
    ("profile", "View your profile"),
    ("support", "Get support"),
]


async def set_bot_commands(bot: Bot) -> None:
    """Set bot commands"""
    await bot.set_my_commands(
        [BotCommand(command=cmd, description=desc) for cmd, desc in COMMANDS]
    )
