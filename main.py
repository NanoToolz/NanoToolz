"""
Telegram Store Bot - Clean rewrite
Main entry point
"""
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from contextlib import asynccontextmanager

from src.config import settings
from src.logger import logger
from src.database import init_db
from src.seed import seed_dummy_data
from src.bot.routers import setup_routers


async def setup_bot():
    """Initialize database and bot setup"""
    logger.info("🗄️  Initializing database...")
    init_db()
    
    logger.info("🌱 Seeding dummy data...")
    seed_dummy_data()


async def main():
    """Main bot entry point"""
    await setup_bot()
    
    logger.info("🤖 Starting bot...")
    bot = Bot(token=settings.BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Setup routers
    setup_routers(dp)
    
    try:
        logger.info("✅ Bot polling started...")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()
        logger.info("Bot stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")