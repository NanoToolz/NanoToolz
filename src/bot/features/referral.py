# ============================================
# FEATURE: Referral Program
# ============================================
# Purpose: Manage user referral program
# Users can earn rewards by referring friends

from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

# ============================================
# ===== MESSAGES SECTION =====
# ============================================

REFERRAL_MENU = (
    "🎁 **Referral Program**\n\n"
    "Earn rewards by inviting friends!\n\n"
    "💰 Earn 10% commission on each referral\n"
    "🎯 No limit on earnings\n"
    "⚡ Instant payouts"
)

REFERRAL_INFO = (
    "📋 **Your Referral Info**\n\n"
    "Referral Code: `{code}`\n"
    "Total Referrals: {count}\n"
    "Total Earned: ${earned:.2f}\n\n"
    "Share your code with friends!"
)

# ============================================
# ===== KEYBOARDS SECTION =====
# ============================================

def get_referral_menu_keyboard() -> InlineKeyboardMarkup:
    """Build referral menu keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 My Referrals", callback_data="my_referrals")],
        [InlineKeyboardButton(text="📋 Copy Link", callback_data="copy_referral")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="back_main")]
    ])

def get_referral_info_keyboard() -> InlineKeyboardMarkup:
    """Build referral info keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back", callback_data="referrals")]
    ])

# ============================================
# ===== HANDLERS SECTION =====
# ============================================

@router.callback_query(F.data == "referrals")
async def referral_menu(callback: CallbackQuery):
    """Show referral menu"""
    keyboard = get_referral_menu_keyboard()
    await callback.message.edit_text(REFERRAL_MENU, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "my_referrals")
async def my_referrals(callback: CallbackQuery):
    """Show my referrals"""
    user_id = callback.from_user.id
    
    # Placeholder - in real app, fetch from database
    text = REFERRAL_INFO.format(
        code=f"REF{user_id}",
        count=0,
        earned=0.0
    )
    
    keyboard = get_referral_info_keyboard()
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "copy_referral")
async def copy_referral(callback: CallbackQuery):
    """Copy referral link"""
    user_id = callback.from_user.id
    referral_code = f"REF{user_id}"
    
    await callback.answer("📋 Referral link copied.", show_alert=True)
    await callback.message.answer(
        f"Your referral link:\n`https://t.me/YourBotName?start={referral_code}`",
        parse_mode="Markdown"
    )
