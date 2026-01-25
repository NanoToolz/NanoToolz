# ============================================
# FEATURE: Start Command & Main Menu
# ============================================
# Purpose: Handle /start command and main menu navigation
# This is the entry point when user starts the bot

# ===== IMPORTS =====
# Import Router for handling messages/callbacks
from aiogram import Router, F
# Import CommandStart filter to detect /start command
from aiogram.filters import CommandStart
# Import message types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, FSInputFile
# Import database for user management
from src.database.json_db import db
# Import logger for logging events
from src.logger import logger
# Import image manager for welcome image
from src.bot.common.image_manager import get_image
# Import datetime for tracking join date
import datetime

# Create router instance - REQUIRED for registering handlers
router = Router()

# ============================================
# ===== MESSAGES SECTION =====
# ============================================
# All text messages used in this feature
# Keep messages organized and easy to find

def get_welcome_text(first_name: str, user_id: int) -> str:
    """
    Generate personalized welcome message
    
    Args:
        first_name: User's first name
        user_id: User's Telegram ID
    
    Returns:
        Formatted welcome message with user info
    """
    return (
        f"👋 **Welcome to NanoToolz!**\n\n"
        f"Hi {first_name}!\n"
        f"Your ID: `{user_id}`\n\n"
        f"🚀 **Instant Delivery**\n"
        f"🔒 **Secure Payments**\n"
        f"💬 **24/7 Support**\n\n"
        f"Select an option below to get started:"
    )

# Main menu text - shown when user clicks "Back"
MAIN_MENU_TEXT = "🏠 **Main Menu**\n\nSelect an option below:"

# ============================================
# ===== KEYBOARDS SECTION =====
# ============================================
# All button layouts used in this feature
# Each function returns a keyboard with buttons

def get_main_keyboard() -> InlineKeyboardMarkup:
    """
    Build main menu keyboard with all options
    
    Returns:
        InlineKeyboardMarkup with main menu buttons
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            # Row 1: Browse Catalog button
            [InlineKeyboardButton(
                text="🛍️ Browse Catalog",
                callback_data="catalog_main"  # Callback when clicked
            )],
            # Row 2: View Cart button
            [InlineKeyboardButton(
                text="🛒 View Cart",
                callback_data="cart_view"
            )],
            # Row 3: Topup Balance button
            [InlineKeyboardButton(
                text="💳 Topup Balance",
                callback_data="topup"
            )],
            # Row 4: Profile button
            [InlineKeyboardButton(
                text="👤 Profile",
                callback_data="profile_view"
            )],
            # Row 5: Admin Panel button (for admins only)
            [InlineKeyboardButton(
                text="🔐 Admin Panel",
                callback_data="admin"
            )]
        ]
    )

# ============================================
# ===== HANDLERS SECTION =====
# ============================================
# All command and callback handlers
# These functions execute when user sends command or clicks button

@router.message(CommandStart())
async def start_command(message: Message):
    """
    Handle /start command
    
    This function runs when user sends /start command
    It registers new users and shows welcome message
    
    Args:
        message: Message object from user
    """
    # Extract user information from message
    user_id = message.from_user.id  # Get user's Telegram ID
    username = message.from_user.username  # Get user's username
    first_name = message.from_user.first_name  # Get user's first name
    
    # Check if user already exists in database
    user = db.get_user(user_id)
    
    # If user is new (no join date), register them
    if not user.get("joined_at"):
        # Update user in database with registration info
        db.update_user(user_id, {
            "username": username,
            "first_name": first_name,
            "joined_at": str(datetime.date.today())  # Record join date
        })
        # Log new user registration
        logger.info(f"New user registered: {user_id}")
    
    # Get personalized welcome message
    welcome_text = get_welcome_text(first_name, user_id)
    
    # Get main menu keyboard
    keyboard = get_main_keyboard()
    
    # Try to send message with welcome image
    image_path = get_image("welcome")
    if image_path:
        # If image exists, send photo with caption
        photo = FSInputFile(image_path)
        await message.answer_photo(
            photo,
            caption=welcome_text,
            reply_markup=keyboard,
            parse_mode="Markdown"  # Enable bold, italic, etc.
        )
    else:
        # If no image, send text message only
        await message.answer(
            welcome_text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )

@router.callback_query(F.data == "back_main")
async def back_to_main(callback: CallbackQuery):
    """
    Handle "Back to Main Menu" button click
    
    This function runs when user clicks back button
    It shows the main menu again
    
    Args:
        callback: Callback query object from button click
    """
    # Get main menu keyboard
    keyboard = get_main_keyboard()
    
    # Edit message to show main menu
    await callback.message.edit_text(
        MAIN_MENU_TEXT,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    
    # Answer callback (removes loading state)
    await callback.answer()
