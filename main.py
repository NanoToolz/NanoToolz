import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from src.config import settings
from src.database import init_db
from src.bot import create_dispatcher, set_bot_commands
from src.seed import seed_dummy_data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def main():
    """Main bot entry point"""
    
    # Initialize database
    logger.info("🗄️  Initializing database...")
    init_db()
    
    # Seed dummy data
    logger.info("🌱 Seeding dummy data...")
    seed_dummy_data()
    
    # Create bot and dispatcher
    logger.info("🤖 Starting bot...")
    bot = Bot(token=settings.BOT_TOKEN)
    dp = create_dispatcher()
    
    # Set bot commands
    await set_bot_commands(bot)
    
    try:
        # Start polling
        logger.info("✅ Bot started! Polling for updates...")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
