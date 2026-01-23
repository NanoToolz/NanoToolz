from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.database import SessionLocal
from src.logger import logger
from src.services.pricing import update_all_product_prices

scheduler = AsyncIOScheduler()


async def update_prices_job() -> None:
    db = SessionLocal()
    try:
        update_all_product_prices(db)
        logger.info("Daily price update completed")
    except Exception as exc:
        logger.error("Price update failed: %s", exc)
    finally:
        db.close()


def start_scheduler() -> None:
    scheduler.add_job(update_prices_job, "cron", hour=0, minute=0)
    scheduler.start()
