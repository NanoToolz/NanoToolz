from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def referral_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📋 Copy Link", callback_data="copy_referral")],
            [InlineKeyboardButton(text="🏆 Leaderboard", callback_data="leaderboard")],
            [InlineKeyboardButton(text="🔙 Back", callback_data="main_menu")],
        ]
    )
