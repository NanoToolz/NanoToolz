from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🛍️ Shop", callback_data="browse")],
            [InlineKeyboardButton(text="🛒 Cart", callback_data="cart")],
            [InlineKeyboardButton(text="💰 Top Up", callback_data="topup")],
            [InlineKeyboardButton(text="👤 Profile", callback_data="profile")],
            [InlineKeyboardButton(text="⭐ Wishlist", callback_data="wishlist")],
            [InlineKeyboardButton(text="🎁 Rewards", callback_data="daily_spin")],
            [InlineKeyboardButton(text="👥 Referrals", callback_data="referrals")],
            [InlineKeyboardButton(text="❓ Help", callback_data="help")],
            [InlineKeyboardButton(text="💬 Support", callback_data="support")],
        ]
    )
