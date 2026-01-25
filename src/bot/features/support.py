# ============================================
# FEATURE: Support Center
# ============================================

from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

SUPPORT_MENU = "📞 **Support Center**\n\nHow can we help you?\n\nContact: @NanoToolzSupport"
SUPPORT_GENERAL = "📧 **General Support**\n\nFor general inquiries, please contact our support team.\n\nResponse time: Usually within 24 hours"
SUPPORT_BILLING = "💳 **Billing Support**\n\nFor payment and billing issues, we're here to help.\n\nContact: billing@nanotoolz.com"
SUPPORT_TECHNICAL = "🔧 **Technical Support**\n\nHaving technical issues? We'll help you resolve them.\n\nContact: tech@nanotoolz.com"

def get_support_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📧 General", callback_data="support_general")],
        [InlineKeyboardButton(text="💳 Billing", callback_data="support_billing")],
        [InlineKeyboardButton(text="🔧 Technical", callback_data="support_technical")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="back_main")]
    ])

def get_back_to_support_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back", callback_data="support")]
    ])

@router.callback_query(F.data == "support")
async def support_menu(callback: CallbackQuery):
    keyboard = get_support_menu_keyboard()
    await callback.message.edit_text(SUPPORT_MENU, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "support_general")
async def support_general(callback: CallbackQuery):
    keyboard = get_back_to_support_keyboard()
    await callback.message.edit_text(SUPPORT_GENERAL, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "support_billing")
async def support_billing(callback: CallbackQuery):
    keyboard = get_back_to_support_keyboard()
    await callback.message.edit_text(SUPPORT_BILLING, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "support_technical")
async def support_technical(callback: CallbackQuery):
    keyboard = get_back_to_support_keyboard()
    await callback.message.edit_text(SUPPORT_TECHNICAL, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()
