from datetime import datetime, date
import random
from aiogram import Router, F
from aiogram.types import CallbackQuery

from src.database import SessionLocal
from src.database.models import DailySpin, User
from src.logger import logger
from src.middleware.rate_limiter import check_rate_limit
from .keyboards import spin_result_keyboard
from .messages import SPIN_ALREADY, SPIN_RESULT_CREDITS, SPIN_RESULT_DISCOUNT

router = Router()


@router.callback_query(F.data == "daily_spin")
async def daily_spin_callback(query: CallbackQuery) -> None:
    """Daily spin"""
    allowed, warn = check_rate_limit(query.from_user.id, with_warning=True)
    if not allowed:
        await query.answer("⏱️ Too many requests. Wait 30 seconds.", show_alert=True)
        return
    if warn:
        await query.answer("⚠️ You're sending too many requests. Slow down.", show_alert=True)

    db = SessionLocal()
    try:
        today = date.today()
        user = db.query(User).filter(User.telegram_id == query.from_user.id).first()
        if not user:
            await query.answer("❌ User not found.", show_alert=True)
            return

        spin_today = (
            db.query(DailySpin)
            .filter(
                DailySpin.user_id == user.id,
                DailySpin.spin_date >= datetime(today.year, today.month, today.day),
            )
            .first()
        )

        if spin_today:
            await query.answer(SPIN_ALREADY, show_alert=True)
            return

        rewards = [
            ("credits", 50),
            ("credits", 100),
            ("credits", 25),
            ("discount", 10),
        ]
        reward_type, reward_value = random.choice(rewards)

        spin = DailySpin(
            user_id=user.id,
            reward_type=reward_type,
            reward_value=reward_value,
        )
        db.add(spin)
        if reward_type == "credits":
            user.credits = float(user.credits) + reward_value
        db.commit()
    except Exception as exc:
        logger.error("Error in daily_spin_callback: %s", exc)
        await query.answer("❌ Something went wrong. Try again.", show_alert=True)
        return
    finally:
        db.close()

    if reward_type == "credits":
        message = SPIN_RESULT_CREDITS.format(reward=reward_value)
    else:
        message = SPIN_RESULT_DISCOUNT.format(reward=reward_value)

    await query.message.edit_text(
        message,
        parse_mode="HTML",
        reply_markup=spin_result_keyboard(),
    )
    await query.answer()
