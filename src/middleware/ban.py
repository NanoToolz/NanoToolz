from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message

from src.database import SessionLocal
from src.database.models import User
from src.logger import logger


class BanMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user = getattr(event, "from_user", None)
        if not user:
            return await handler(event, data)

        db = SessionLocal()
        try:
            db_user = db.query(User).filter(User.telegram_id == user.id).first()
            if db_user and db_user.is_banned:
                if isinstance(event, CallbackQuery):
                    await event.answer("⛔ You are banned. Contact support.", show_alert=True)
                elif isinstance(event, Message):
                    await event.answer("⛔ You are banned. Contact support.")
                logger.info("Blocked banned user %s", user.id)
                return
        except Exception as exc:
            logger.error("Ban check failed: %s", exc)
        finally:
            db.close()

        return await handler(event, data)
