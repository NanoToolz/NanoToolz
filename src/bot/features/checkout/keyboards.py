from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def payment_method_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🪙 USDT (TRON)", callback_data="pay_usdt_tron")],
            [InlineKeyboardButton(text="🪙 Litecoin (LTC)", callback_data="pay_ltc")],
            [InlineKeyboardButton(text="💳 Pay with Credits", callback_data="pay_credits")],
            [InlineKeyboardButton(text="🔙 Back to Cart", callback_data="cart")],
        ]
    )


def payment_action_keyboard(payment_ref: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ I Paid", callback_data=f"confirm_pay_{payment_ref}")],
            [InlineKeyboardButton(text="❌ Cancel", callback_data=f"cancel_pay_{payment_ref}")],
        ]
    )
