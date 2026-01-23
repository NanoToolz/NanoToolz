from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def support_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📧 General", callback_data="support_general")],
            [InlineKeyboardButton(text="❌ Order Issue", callback_data="support_order")],
            [InlineKeyboardButton(text="🐛 Bug Report", callback_data="support_bug")],
            [InlineKeyboardButton(text="🔙 Back", callback_data="main_menu")],
        ]
    )
