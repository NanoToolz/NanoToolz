from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def categories_keyboard(categories) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=f"{cat.emoji} {cat.name}", callback_data=f"category_{cat.id}")]
        for cat in categories
    ]
    buttons.append([InlineKeyboardButton(text="🔙 Back", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def products_keyboard(products) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=f"📦 {product.name}", callback_data=f"product_{product.id}")]
        for product in products
    ]
    buttons.append([InlineKeyboardButton(text="🔙 Back", callback_data="browse")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def product_detail_keyboard(product_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="➕ Add to Cart", callback_data=f"add_cart_{product_id}"),
                InlineKeyboardButton(text="❤️ Wishlist", callback_data=f"wishlist_add_{product_id}"),
            ],
            [InlineKeyboardButton(text="📋 Reviews", callback_data=f"reviews_{product_id}")],
            [
                InlineKeyboardButton(text="🔙 Back", callback_data="browse"),
                InlineKeyboardButton(text="🏠 Home", callback_data="main_menu"),
            ],
        ]
    )


def review_rating_keyboard(product_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="1⭐", callback_data=f"review_rate_{product_id}_1"),
                InlineKeyboardButton(text="2⭐", callback_data=f"review_rate_{product_id}_2"),
                InlineKeyboardButton(text="3⭐", callback_data=f"review_rate_{product_id}_3"),
                InlineKeyboardButton(text="4⭐", callback_data=f"review_rate_{product_id}_4"),
                InlineKeyboardButton(text="5⭐", callback_data=f"review_rate_{product_id}_5"),
            ],
            [InlineKeyboardButton(text="🔙 Back", callback_data=f"product_{product_id}")],
        ]
    )
