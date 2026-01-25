# ============================================
# FEATURE: Help & FAQ
# ============================================
# Purpose: Provide help and frequently asked questions
# Users can browse help topics and get support information

# ===== IMPORTS =====
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

# ============================================
# ===== MESSAGES SECTION =====
# ============================================

# Help menu intro
HELP_MENU = "❓ Help Center\n\nNeed assistance? Choose a topic:"

# How to shop guide
HELP_SHOP = (
    "🛍️ How to Shop\n\n"
    "1️⃣ Browse Catalog - View all categories\n"
    "2️⃣ Select Product - Click on product to see details\n"
    "3️⃣ Add to Cart - Click 'Add to Cart' button\n"
    "4️⃣ View Cart - Check your items\n"
    "5️⃣ Checkout - Choose payment method\n"
    "6️⃣ Confirm - Complete your order\n\n"
    "That's it! 🎉"
)

# Payment methods guide
HELP_PAYMENT = (
    "💳 Payment Methods\n\n"
    "We accept:\n\n"
    "💰 Account Credits\n"
    "   - Top up your account balance\n"
    "   - Pay directly from wallet\n\n"
    "💳 Credit/Debit Card\n"
    "   - Secure payment processing\n"
    "   - Instant confirmation\n\n"
    "All payments are secure and encrypted."
)

# Delivery information guide
HELP_DELIVERY = (
    "📦 Delivery Information\n\n"
    "Order Processing:\n"
    "⏰ Instant - Most items delivered immediately\n"
    "⏰ 24 hours - Some items within 24 hours\n\n"
    "Delivery Methods:\n"
    "📧 Email - Digital products via email\n"
    "💬 Chat - Direct message in Telegram\n"
    "🔗 Link - Access link provided\n\n"
    "Check your order status in Profile → Order History"
)

# ============================================
# ===== KEYBOARDS SECTION =====
# ============================================

def get_help_menu_keyboard() -> InlineKeyboardMarkup:
    """Build help menu keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❓ How to Shop", callback_data="help_shop")],
        [InlineKeyboardButton(text="💳 Payment Methods", callback_data="help_payment")],
        [InlineKeyboardButton(text="📦 Delivery Info", callback_data="help_delivery")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="back_main")]
    ])

def get_back_to_help_keyboard() -> InlineKeyboardMarkup:
    """Build back to help keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back", callback_data="help_main")]
    ])

# ============================================
# ===== HANDLERS SECTION =====
# ============================================

@router.callback_query(F.data == "help_main")
async def help_menu(callback: CallbackQuery):
    """Show help menu"""
    keyboard = get_help_menu_keyboard()
    await callback.message.edit_text(HELP_MENU, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data == "help_shop")
async def help_shop(callback: CallbackQuery):
    """Show how to shop guide"""
    keyboard = get_back_to_help_keyboard()
    await callback.message.edit_text(HELP_SHOP, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data == "help_payment")
async def help_payment(callback: CallbackQuery):
    """Show payment methods guide"""
    keyboard = get_back_to_help_keyboard()
    await callback.message.edit_text(HELP_PAYMENT, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data == "help_delivery")
async def help_delivery(callback: CallbackQuery):
    """Show delivery information guide"""
    keyboard = get_back_to_help_keyboard()
    await callback.message.edit_text(HELP_DELIVERY, reply_markup=keyboard)
    await callback.answer()
