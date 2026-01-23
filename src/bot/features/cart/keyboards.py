from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def cart_keyboard(items) -> InlineKeyboardMarkup:
    buttons = []
    for item in items:
        buttons.append(
            [
                InlineKeyboardButton(text="➖", callback_data=f"cart_dec_{item.id}"),
                InlineKeyboardButton(text=f"{item.product.name} x{item.quantity}", callback_data="noop"),
                InlineKeyboardButton(text="➕", callback_data=f"cart_inc_{item.id}"),
                InlineKeyboardButton(text="❌", callback_data=f"cart_del_{item.id}"),
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(text="💳 Checkout", callback_data="checkout"),
            InlineKeyboardButton(text="🧹 Clear Cart", callback_data="cart_clear"),
        ]
    )
    buttons.append([InlineKeyboardButton(text="🏠 Home", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
