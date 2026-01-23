from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def wishlist_keyboard(items) -> InlineKeyboardMarkup:
    buttons = []
    for item in items:
        buttons.append(
            [
                InlineKeyboardButton(text=f"❌ Remove {item.product.name}", callback_data=f"wishlist_del_{item.id}"),
                InlineKeyboardButton(text="🛒 Add to Cart", callback_data=f"wishlist_cart_{item.product.id}"),
            ]
        )
    buttons.append([InlineKeyboardButton(text="📚 Browse Store", callback_data="browse")])
    buttons.append([InlineKeyboardButton(text="🏠 Home", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
