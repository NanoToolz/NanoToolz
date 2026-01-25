# ============================================
# FEATURE: Balance Topup
# ============================================
# Purpose: Allow users to add funds to their account
# Supports multiple payment methods and amounts

# ===== IMPORTS =====
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from src.database.json_db import db

router = Router()

# ============================================
# ===== MESSAGES SECTION =====
# ============================================

# Topup intro message
TOPUP_INTRO = (
    "💳 **Add Funds**\n\n"
    "Select the amount you want to topup:\n"
    "Minimum: $10\n"
    "Maximum: $1000"
)

# Payment method selection message
TOPUP_PAYMENT_METHOD = (
    "💳 **Topup Amount: ${amount}**\n\n"
    "Select Payment Gateway:"
)

# Success message after topup
TOPUP_SUCCESS = (
    "✅ **Payment Successful!**\n\n"
    "💰 Added: **${amount}**\n"
    "💳 New Balance: **${balance:.2f}**"
)

# ============================================
# ===== KEYBOARDS SECTION =====
# ============================================

def get_topup_amounts_keyboard() -> InlineKeyboardMarkup:
    """
    Build keyboard with topup amount options
    
    Returns:
        Keyboard with predefined amounts
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        # Row 1: $10, $20, $50
        [
            InlineKeyboardButton(text="$10", callback_data="topup_10"),
            InlineKeyboardButton(text="$20", callback_data="topup_20"),
            InlineKeyboardButton(text="$50", callback_data="topup_50")
        ],
        # Row 2: $100, $500
        [
            InlineKeyboardButton(text="$100", callback_data="topup_100"),
            InlineKeyboardButton(text="$500", callback_data="topup_500")
        ],
        # Row 3: Back button
        [InlineKeyboardButton(text="⬅️ Back", callback_data="profile_view")]
    ])

def get_payment_method_keyboard(amount: int) -> InlineKeyboardMarkup:
    """
    Build keyboard with payment method options
    
    Args:
        amount: Topup amount in dollars
    
    Returns:
        Keyboard with payment methods
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Crypto (Mock)", callback_data=f"pay_crypto_{amount}")],
        [InlineKeyboardButton(text="💳 Card (Mock)", callback_data=f"pay_card_{amount}")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="topup")]
    ])

def get_topup_success_keyboard() -> InlineKeyboardMarkup:
    """
    Build keyboard after successful topup
    
    Returns:
        Keyboard with profile and shop buttons
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 View Profile", callback_data="profile_view")],
        [InlineKeyboardButton(text="🛍️ Shop Now", callback_data="catalog_main")]
    ])

# ============================================
# ===== HANDLERS SECTION =====
# ============================================

@router.callback_query(F.data == "topup")
async def start_topup(callback: CallbackQuery):
    """
    Start topup process
    
    Shows available topup amounts
    """
    # Build keyboard with amounts
    keyboard = get_topup_amounts_keyboard()
    
    # Edit message to show topup options
    await callback.message.edit_text(TOPUP_INTRO, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data.startswith("topup_"))
async def select_payment_method(callback: CallbackQuery):
    """
    Select payment method for topup
    
    Extracts amount from callback and shows payment options
    """
    try:
        # Extract amount from callback_data
        # Format: "topup_50" -> extract "50"
        amount = int(callback.data.split("_")[1])
    except (ValueError, IndexError):
        await callback.answer("Invalid amount", show_alert=True)
        return
    
    # Build message with selected amount
    text = TOPUP_PAYMENT_METHOD.format(amount=amount)
    
    # Build keyboard with payment methods
    keyboard = get_payment_method_keyboard(amount)
    
    # Edit message to show payment methods
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data.startswith("pay_"))
async def process_mock_topup(callback: CallbackQuery):
    """
    Process mock topup payment
    
    Adds funds to user's account (mock payment)
    """
    # Split callback_data to extract payment type and amount
    parts = callback.data.split("_")
    
    try:
        # Extract amount from callback_data
        # Format: "pay_crypto_50" -> extract "50"
        amount = int(parts[2])
    except (ValueError, IndexError):
        await callback.answer("Invalid request", show_alert=True)
        return
    
    # SECURITY: Validate amount to prevent exploits
    if amount <= 0 or amount > 10000:
        await callback.answer("Invalid amount", show_alert=True)
        return
    
    # Get user ID
    user_id = callback.from_user.id
    
    # Get user data
    user = db.get_user(user_id)
    
    # Calculate new balance
    new_balance = user['balance'] + amount
    
    # Update user balance in database
    db.update_user(user_id, {"balance": new_balance})
    
    # Build success message
    text = TOPUP_SUCCESS.format(amount=amount, balance=new_balance)
    
    # Build keyboard
    keyboard = get_topup_success_keyboard()
    
    # Edit message to show success
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()
