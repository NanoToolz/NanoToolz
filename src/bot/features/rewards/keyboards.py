from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def spin_result_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🛍️ Shop", callback_data="browse")],
            [InlineKeyboardButton(text="🏠 Home", callback_data="main_menu")],
        ]
    )
