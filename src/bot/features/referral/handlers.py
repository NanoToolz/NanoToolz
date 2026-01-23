from aiogram import Router, F
from aiogram.types import CallbackQuery

from src.database import SessionLocal
from src.database.models import User, Referral
from src.logger import logger
from src.middleware.rate_limiter import check_rate_limit
from .keyboards import referral_keyboard
from .messages import REFERRAL_MESSAGE

router = Router()


@router.callback_query(F.data == "referrals")
async def referrals_callback(query: CallbackQuery) -> None:
    """Show referral program"""
    allowed, warn = check_rate_limit(query.from_user.id, with_warning=True)
    if not allowed:
        await query.answer("⏱️ Too many requests. Wait 30 seconds.", show_alert=True)
        return
    if warn:
        await query.answer("⚠️ You're sending too many requests. Slow down.", show_alert=True)

    user_id = query.from_user.id
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_id == user_id).first()
        referral_code = user.referral_code if user else "N/A"
        if user:
            referrals = db.query(Referral).filter(Referral.referrer_id == user.id).all()
            referrals_count = len(referrals)
            earned = sum(float(r.earnings) for r in referrals)
        else:
            referrals_count = 0
            earned = 0.0
    except Exception as exc:
        logger.error("Error in referrals_callback: %s", exc)
        await query.answer("❌ Something went wrong. Try again.", show_alert=True)
        return
    finally:
        db.close()

    await query.message.edit_text(
        REFERRAL_MESSAGE.format(
            referral_code=referral_code,
            referrals=referrals_count,
            earned=earned,
        ),
        parse_mode="HTML",
        reply_markup=referral_keyboard(),
    )
    await query.answer()


@router.callback_query(F.data == "copy_referral")
async def copy_referral_placeholder(query: CallbackQuery) -> None:
    allowed, warn = check_rate_limit(query.from_user.id, with_warning=True)
    if not allowed:
        await query.answer("⏱️ Too many requests. Wait 30 seconds.", show_alert=True)
        return
    if warn:
        await query.answer("⚠️ You're sending too many requests. Slow down.", show_alert=True)

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_id == query.from_user.id).first()
        referral_code = user.referral_code if user else ""
    except Exception as exc:
        logger.error("Error in copy_referral: %s", exc)
        await query.answer("❌ Something went wrong. Try again.", show_alert=True)
        return
    finally:
        db.close()
    if referral_code:
        await query.answer("📋 Referral link copied.", show_alert=True)
        await query.message.answer(
            f"Your link:\nhttps://t.me/YourBotName?start={referral_code}"
        )
    else:
        await query.answer("Referral link not available.", show_alert=True)


@router.callback_query(F.data == "leaderboard")
async def leaderboard_placeholder(query: CallbackQuery) -> None:
    allowed = check_rate_limit(query.from_user.id)
    if not allowed:
        await query.answer("⏱️ Too many requests. Wait 30 seconds.", show_alert=True)
        return
    await query.answer("🏆 Leaderboard is coming soon.", show_alert=True)
