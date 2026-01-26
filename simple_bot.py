# ============================================
# NANOTOOLZ BOT - SIMPLE VERSION
# ============================================
# Sab kuch ek file mein!

import os
import asyncio
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage

# Load .env file
load_dotenv()

# Settings
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_IDS = [int(id.strip()) for id in os.getenv("ADMIN_IDS", "").split(",") if id.strip()]

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = Router()

# ============================================
# DATABASE (Simple Dictionary)
# ============================================
users = {}
products = []
orders = []

# ============================================
# START COMMAND
# ============================================

@router.message(CommandStart())
async def start_command(message: Message):
    """Handle /start command"""
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    
    # Save user
    if user_id not in users:
        users[user_id] = {
            "name": first_name,
            "balance": 0,
            "cart": {}
        }
        logger.info(f"New user: {user_id}")
    
    # Welcome message
    text = (
        f"👋 **Welcome to NanoToolz!**\n\n"
        f"Hi {first_name}!\n\n"
        f"🚀 **Instant Delivery**\n"
        f"🔒 **Secure Payments**\n"
        f"💬 **24/7 Support**\n\n"
        f"Select an option:"
    )
    
    # Buttons
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍️ Shop", callback_data="shop")],
        [InlineKeyboardButton(text="🛒 Cart", callback_data="cart")],
        [InlineKeyboardButton(text="👤 Profile", callback_data="profile")],
    ])
    
    await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")

# ============================================
# SHOP
# ============================================

@router.callback_query(F.data == "shop")
async def shop_handler(callback: CallbackQuery):
    """Show products"""
    text = "🛍️ **Shop**\n\nProducts coming soon!"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back", callback_data="back")]
    ])
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()

# ============================================
# CART
# ============================================

@router.callback_query(F.data == "cart")
async def cart_handler(callback: CallbackQuery):
    """Show cart"""
    text = "🛒 **Cart**\n\nYour cart is empty"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back", callback_data="back")]
    ])
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()

# ============================================
# PROFILE
# ============================================

@router.callback_query(F.data == "profile")
async def profile_handler(callback: CallbackQuery):
    """Show profile"""
    user_id = callback.from_user.id
    user = users.get(user_id, {})
    
    text = (
        f"👤 **Profile**\n\n"
        f"Name: {user.get('name', 'Unknown')}\n"
        f"Balance: ${user.get('balance', 0)}\n"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back", callback_data="back")]
    ])
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()

# ============================================
# BACK BUTTON
# ============================================

@router.callback_query(F.data == "back")
async def back_handler(callback: CallbackQuery):
    """Go back to main menu"""
    text = "🏠 **Main Menu**\n\nSelect an option:"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍️ Shop", callback_data="shop")],
        [InlineKeyboardButton(text="🛒 Cart", callback_data="cart")],
        [InlineKeyboardButton(text="👤 Profile", callback_data="profile")],
    ])
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()

# ============================================
# MAIN FUNCTION
# ============================================

async def main():
    """Start bot"""
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    
    await bot.delete_webhook(drop_pending_updates=True)
    print("🤖 Bot is running...")
    await dp.start_polling(bot)

# ============================================
# RUN BOT
# ============================================

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped")
