from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from src.database.json_db import db
from src.logger import logger

router = Router()

@router.message(CommandStart())
async def start_command(message: Message):
    """Handle /start command"""
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    
    # Get or create user
    user = db.get_user(user_id)
    if not user.get("joined_at"):
        import datetime
        db.update_user(user_id, {
            "username": username,
            "first_name": first_name,
            "joined_at": str(datetime.date.today())
        })
        logger.info(f"New user registered: {user_id}")
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🛍️ Browse Catalog", callback_data="catalog_main")],
            [InlineKeyboardButton(text="🛒 View Cart", callback_data="cart_view")],
            [InlineKeyboardButton(text="💳 Topup Balance", callback_data="topup")],
            [InlineKeyboardButton(text="👤 Profile", callback_data="profile_view")],
            # [InlineKeyboardButton(text="🎁 Daily Spin", callback_data="daily_spin")], # TODO
            # [InlineKeyboardButton(text="📞 Support", callback_data="support")], # TODO
            [InlineKeyboardButton(text="🔐 Admin Panel", callback_data="admin")]
        ]
    )
    
    welcome_text = (
        f"👋 **Welcome to NanoToolz!**\n\n"
        f"Hi {first_name}!\n"
        f"Your ID: `{user_id}`\n\n"
        f"🚀 **Instant Delivery**\n"
        f"🔒 **Secure Payments**\n"
        f"💬 **24/7 Support**\n\n"
        f"Select an option below to get started:"
    )
    
    await message.answer(welcome_text, reply_markup=keyboard, parse_mode="Markdown")

@router.callback_query(F.data == "back_main")
async def back_to_main(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="�️ Browse Catalog", callback_data="catalog_main")],
            [InlineKeyboardButton(text="🛒 View Cart", callback_data="cart_view")],
            [InlineKeyboardButton(text="� Topup Balance", callback_data="topup")],
            [InlineKeyboardButton(text="👤 Profile", callback_data="profile_view")],
            [InlineKeyboardButton(text="🔐 Admin Panel", callback_data="admin_panel")]
        ]
    )
    
    text = "🏠 **Main Menu**\n\nSelect an option below:"
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()