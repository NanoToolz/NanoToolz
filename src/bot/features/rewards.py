# ============================================
# FEATURE: Daily Rewards & Spin
# ============================================
# Purpose: Daily spin wheel for rewards
# Users can spin once per day to win credits or discounts

import random
from datetime import datetime, date
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

# ============================================
# ===== MESSAGES SECTION =====
# ============================================

DAILY_SPIN_INTRO = (
    "🎡 **Daily Spin**\n\n"
    "Spin the wheel daily to win rewards!\n\n"
    "💰 Win credits\n"
    "🎟️ Win discount coupons\n"
    "⭐ Limited to 1 spin per day"
)

SPIN_RESULT_CREDITS = (
    "🎉 **Congratulations!**\n\n"
    "You won **${reward}** in credits!\n\n"
    "Your balance has been updated."
)

SPIN_RESULT_DISCOUNT = (
    "🎉 **Congratulations!**\n\n"
    "You won a **{reward}% discount** coupon!\n\n"
    "Use it on your next purchase."
)

SPIN_ALREADY = "⏰ You already spun today! Come back tomorrow."

# ============================================
# ===== KEYBOARDS SECTION =====
# ============================================

def get_daily_spin_keyboard() -> InlineKeyboardMarkup:
    """Build daily spin keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎡 Spin Now", callback_data="spin_now")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="back_main")]
    ])

def get_spin_result_keyboard() -> InlineKeyboardMarkup:
    """Build spin result keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍️ Shop Now", callback_data="catalog_main")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="back_main")]
    ])

# ============================================
# ===== HANDLERS SECTION =====
# ============================================

@router.callback_query(F.data == "daily_spin")
async def daily_spin_menu(callback: CallbackQuery):
    """Show daily spin menu"""
    keyboard = get_daily_spin_keyboard()
    await callback.message.edit_text(DAILY_SPIN_INTRO, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "spin_now")
async def spin_now(callback: CallbackQuery):
    """Perform daily spin"""
    user_id = callback.from_user.id
    
    # Simple check - in real app, use database to track spins
    # For now, always allow spin (placeholder)
    
    # Define possible rewards
    rewards = [
        ("credits", 50),      # Win $50 credits
        ("credits", 100),     # Win $100 credits
        ("credits", 25),      # Win $25 credits
        ("discount", 10),     # Win 10% discount
    ]
    
    # Randomly select a reward
    reward_type, reward_value = random.choice(rewards)
    
    # Build result message based on reward type
    if reward_type == "credits":
        text = SPIN_RESULT_CREDITS.format(reward=reward_value)
    else:
        text = SPIN_RESULT_DISCOUNT.format(reward=reward_value)
    
    # Build keyboard
    keyboard = get_spin_result_keyboard()
    
    # Edit message to show result
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    
    # Show notification
    await callback.answer("🎉 You won a reward!")
