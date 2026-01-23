from aiogram import Router, F
from aiogram.types import CallbackQuery

from src.database import SessionLocal
from src.database.models import User, Referral
from .keyboards import referral_keyboard
from .messages import REFERRAL_MESSAGE

router = Router()


@router.callback_query(F.data == "referrals")
async def referrals_callback(query: CallbackQuery) -> None:
    """Show referral program"""
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
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_id == query.from_user.id).first()
        referral_code = user.referral_code if user else ""
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
    await query.answer("🏆 Leaderboard is coming soon.", show_alert=True)
