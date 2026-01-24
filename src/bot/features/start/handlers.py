"""
Start command handler - entry point for users
"""
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.orm import Session

from src.database import get_db
from src.database.models import User
from src.logger import logger

router = Router()

@router.message(CommandStart())
async def start_command(message: Message):
    """Handle /start command"""
    db: Session = next(get_db())
    
    # Check if user exists
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    
    if not user:
        # Create new user
        user = User(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name
        )
        db.add(user)
        db.commit()
        logger.info(f"New user registered: {message.from_user.id}")
    
    # Send welcome message
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🛍️ Browse Catalog", callback_data="catalog_main")],
            [InlineKeyboardButton(text="🛒 View Cart", callback_data="cart_view")],
            [InlineKeyboardButton(text="� Topup", callback_data="topup")],
            [InlineKeyboardButton(text="🎁 Daily Spin", callback_data="daily_spin")],
            [InlineKeyboardButton(text="�👤 Profile", callback_data="profile_view")],
            [InlineKeyboardButton(text="📞 Support", callback_data="support")],
            [InlineKeyboardButton(text="❓ Help", callback_data="help_main")],
            [InlineKeyboardButton(text="🔐 Admin Panel", callback_data="admin_panel")]
        ]
    )
    
    welcome_text = (
        f"Welcome to NanoToolz Store! 🎉\n\n"
        f"Hi {message.from_user.first_name or 'User'}!\n\n"
        f"Browse our catalog, add items to cart, and checkout easily.\n\n"
        f"What would you like to do?"
    )
    
    await message.answer(welcome_text, reply_markup=keyboard)
    db.close()