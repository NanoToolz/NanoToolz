from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def topup_amount_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💵 $5", callback_data="topup_5")],
            [InlineKeyboardButton(text="💵 $10", callback_data="topup_10")],
            [InlineKeyboardButton(text="💵 $25", callback_data="topup_25")],
            [InlineKeyboardButton(text="💵 $50", callback_data="topup_50")],
            [InlineKeyboardButton(text="💵 $100", callback_data="topup_100")],
            [InlineKeyboardButton(text="⬅️ Back", callback_data="main_menu")],
        ]
    )


def topup_confirm_keyboard(payment_ref: str, amount: float) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ I Paid",
                    callback_data=f"confirm_topup_{payment_ref}_{amount}",
                )
            ],
            [InlineKeyboardButton(text="❌ Cancel", callback_data="main_menu")],
        ]
    )
