from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from src.config import settings
from src.bot.routers import setup_routers


async def start_bot():
    bot = Bot(token=settings.BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    setup_routers(dp)

    await bot.delete_webhook(drop_pending_updates=True)

    try:
        print("Bot is running...")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
