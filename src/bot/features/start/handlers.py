import uuid
from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, CallbackQuery

from src.database import SessionLocal
from src.database.models import User, Referral
from src.bot.common.keyboards import main_menu_keyboard
from src.services.settings import get_setting
from .messages import welcome_message

router = Router()


@router.message(Command("start"))
async def start_command(message: Message, command: CommandObject) -> None:
    """Handle /start command"""
    user_id = message.from_user.id
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_id == user_id).first()
        if not user:
            referral_code = f"ref_{uuid.uuid4().hex[:8]}"
            user = User(
                telegram_id=user_id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                referral_code=referral_code,
            )
            db.add(user)
            db.commit()
        if command.args and not user.referred_by_id:
            ref_user = (
                db.query(User).filter(User.referral_code == command.args).first()
            )
            if ref_user and ref_user.id != user.id:
                user.referred_by_id = ref_user.id
                db.add(
                    Referral(
                        referrer_id=ref_user.id,
                        referred_user_id=user.id,
                        earnings=0,
                    )
                )
                db.commit()
        store_name = get_setting(db, "store_name", "NanoToolz Store") or "NanoToolz Store"
    finally:
        db.close()

    await message.answer(
        welcome_message(store_name),
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(),
    )


@router.callback_query(F.data == "main_menu")
async def main_menu_callback(query: CallbackQuery) -> None:
    """Return to main menu"""
    db = SessionLocal()
    try:
        store_name = get_setting(db, "store_name", "NanoToolz Store") or "NanoToolz Store"
    finally:
        db.close()
    await query.message.edit_text(
        welcome_message(store_name),
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(),
    )
    await query.answer()


@router.message()
async def fallback_handler(message: Message) -> None:
    """Fallback for unhandled messages"""
    if message.text and message.text.startswith("/"):
        return
    await message.answer(
        "I didn't understand that. Use /help for available commands or choose from the menu.",
        reply_markup=main_menu_keyboard(),
    )
