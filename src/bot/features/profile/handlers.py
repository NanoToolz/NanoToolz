from aiogram import Router, F
from aiogram.types import CallbackQuery

from src.database import SessionLocal
from src.database.models import User, Referral
from .keyboards import profile_keyboard, settings_keyboard, currency_keyboard, language_keyboard
from .messages import PROFILE_MESSAGE, SETTINGS_MESSAGE, CURRENCY_MESSAGE, LANGUAGE_MESSAGE

router = Router()


async def _show_settings(query: CallbackQuery, answer: bool = True) -> None:
    await query.message.edit_text(
        SETTINGS_MESSAGE,
        parse_mode="HTML",
        reply_markup=settings_keyboard(),
    )
    if answer:
        await query.answer()


@router.callback_query(F.data == "profile")
async def profile_callback(query: CallbackQuery) -> None:
    """Show user profile"""
    user_id = query.from_user.id
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_id == user_id).first()
        if user:
            username = user.username or "N/A"
            credits = float(user.credits)
            referral_code = user.referral_code or "N/A"
            orders_count = len(user.orders)
            referrals_count = db.query(Referral).filter(Referral.referrer_id == user.id).count()
        else:
            username = "N/A"
            credits = 0
            referral_code = "N/A"
            orders_count = 0
            referrals_count = 0
    finally:
        db.close()

    await query.message.edit_text(
        PROFILE_MESSAGE.format(
            username=username,
            credits=credits,
            referral_code=referral_code,
            referrals=referrals_count,
            orders=orders_count,
        ),
        parse_mode="HTML",
        reply_markup=profile_keyboard(),
    )
    await query.answer()


@router.callback_query(F.data == "settings")
async def settings_callback(query: CallbackQuery) -> None:
    """User settings"""
    await _show_settings(query, answer=True)


@router.callback_query(F.data == "currency")
async def currency_settings(query: CallbackQuery) -> None:
    """Change currency setting"""
    await query.message.edit_text(
        CURRENCY_MESSAGE,
        parse_mode="HTML",
        reply_markup=currency_keyboard(),
    )
    await query.answer()


@router.callback_query(F.data.startswith("set_currency_"))
async def set_currency(query: CallbackQuery) -> None:
    """Set user currency"""
    currency = query.data.split("_")[2]
    user_id = query.from_user.id
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_id == user_id).first()
        if user:
            user.currency = currency
            db.commit()
    finally:
        db.close()

    await query.answer(f"✅ Currency changed to {currency}")
    await _show_settings(query, answer=False)


@router.callback_query(F.data == "language")
async def language_settings(query: CallbackQuery) -> None:
    await query.message.edit_text(
        LANGUAGE_MESSAGE,
        parse_mode="HTML",
        reply_markup=language_keyboard(),
    )
    await query.answer()


@router.callback_query(F.data.startswith("set_language_"))
async def set_language(query: CallbackQuery) -> None:
    language = query.data.split("_")[2]
    user_id = query.from_user.id
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_id == user_id).first()
        if user:
            user.language = language
            db.commit()
    finally:
        db.close()

    await query.answer(f"✅ Language set to {language}")
    await _show_settings(query, answer=False)


@router.callback_query(F.data == "stats")
async def stats_placeholder(query: CallbackQuery) -> None:
    await query.answer("📊 Stats are coming soon.", show_alert=True)


@router.callback_query(F.data == "notifications")
async def notifications_placeholder(query: CallbackQuery) -> None:
    await query.answer("🔔 Notifications settings are coming soon.", show_alert=True)
