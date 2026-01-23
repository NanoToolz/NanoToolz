from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📚 Browse Store", callback_data="browse")],
            [
                InlineKeyboardButton(text="🛒 Cart (0)", callback_data="cart"),
                InlineKeyboardButton(text="⭐ Wishlist", callback_data="wishlist"),
            ],
            [
                InlineKeyboardButton(text="👤 Profile", callback_data="profile"),
                InlineKeyboardButton(text="🆘 Support", callback_data="support"),
            ],
            [
                InlineKeyboardButton(text="🎡 Daily Spin", callback_data="daily_spin"),
                InlineKeyboardButton(text="🎁 Referrals", callback_data="referrals"),
            ],
        ]
    )
