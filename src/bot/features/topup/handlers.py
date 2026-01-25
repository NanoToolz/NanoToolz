from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from src.database.json_db import db

router = Router()

@router.callback_query(F.data == "topup")
async def start_topup(callback: CallbackQuery):
    text = (
        "💳 **Add Funds**\n\n"
        "Select the amount you want to topup:\n"
        "Minimum: $10\n"
        "Maximum: $1000"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="$10", callback_data="topup_10"),
            InlineKeyboardButton(text="$20", callback_data="topup_20"),
            InlineKeyboardButton(text="$50", callback_data="topup_50")
        ],
        [
            InlineKeyboardButton(text="$100", callback_data="topup_100"),
            InlineKeyboardButton(text="$500", callback_data="topup_500")
        ],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="profile_view")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data.startswith("topup_"))
async def select_payment_method(callback: CallbackQuery):
    amount = int(callback.data.split("_")[1])
    
    text = (
        f"💳 **Topup Amount: ${amount}**\n\n"
        "Select Payment Gateway:"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Crypto (Mock)", callback_data=f"pay_crypto_{amount}")],
        [InlineKeyboardButton(text="💳 Card (Mock)", callback_data=f"pay_card_{amount}")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="topup")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")

@router.callback_query(F.data.startswith("pay_"))
async def process_mock_topup(callback: CallbackQuery):
    parts = callback.data.split("_")
    # type = parts[1] (crypto/card)
    try:
        amount = int(parts[2])
    except (ValueError, IndexError):
        await callback.answer("Invalid request", show_alert=True)
        return
    
    # SECURITY FIX: Prevent negative topup exploit
    if amount <= 0 or amount > 10000:
        await callback.answer("Invalid amount", show_alert=True)
        return
        
    user_id = callback.from_user.id
    
    user = db.get_user(user_id)
    new_balance = user['balance'] + amount
    
    db.update_user(user_id, {"balance": new_balance})
    
    text = (
        f"✅ **Payment Successful!**\n\n"
        f"💰 Added: **${amount}**\n"
        f"💳 New Balance: **${new_balance:.2f}**"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 View Profile", callback_data="profile_view")],
        [InlineKeyboardButton(text="🛍️ Shop Now", callback_data="catalog_main")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")