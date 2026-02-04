from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from src.database import db

router = Router()

WISHLIST_EMPTY = "Your Wishlist is Empty\n\nAdd products to your wishlist to save them for later!"
WISHLIST_TITLE = "Your Wishlist\n\n"


def get_empty_wishlist_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Browse Catalog", callback_data="catalog_main")],
        [InlineKeyboardButton(text="Back", callback_data="back_main")]
    ])


def get_wishlist_keyboard(wishlist_items: list) -> InlineKeyboardMarkup:
    buttons = []

    for item in wishlist_items:
        product = item.get("products")
        if product:
            buttons.append([
                InlineKeyboardButton(
                    text=f"{product['name']} - ${product['price']}",
                    callback_data=f"prod_{product['id']}"
                ),
                InlineKeyboardButton(
                    text="X",
                    callback_data=f"wishlist_del_{product['id']}"
                )
            ])

    buttons.append([InlineKeyboardButton(text="Browse Catalog", callback_data="catalog_main")])
    buttons.append([InlineKeyboardButton(text="Back", callback_data="back_main")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.callback_query(F.data == "wishlist")
async def wishlist_view(callback: CallbackQuery):
    user_id = callback.from_user.id
    db.get_or_create_user(user_id, callback.from_user.username, callback.from_user.first_name)

    wishlist = db.get_wishlist(user_id)

    if not wishlist:
        keyboard = get_empty_wishlist_keyboard()
        try:
            await callback.message.edit_text(WISHLIST_EMPTY, reply_markup=keyboard, parse_mode="Markdown")
        except Exception:
            await callback.message.delete()
            await callback.message.answer(WISHLIST_EMPTY, reply_markup=keyboard, parse_mode="Markdown")
        await callback.answer()
        return

    text = WISHLIST_TITLE

    for item in wishlist:
        product = item.get("products")
        if product:
            stock = db.get_stock_count(product['id'])
            status = "In Stock" if stock > 0 else "Out of Stock"
            text += f"- {product['name']} - ${product['price']} ({status})\n"

    keyboard = get_wishlist_keyboard(wishlist)

    try:
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    except Exception:
        await callback.message.delete()
        await callback.message.answer(text, reply_markup=keyboard, parse_mode="Markdown")

    await callback.answer()


@router.callback_query(F.data.startswith("wishlist_add_"))
async def wishlist_add(callback: CallbackQuery):
    try:
        product_id = int(callback.data.split("_")[2])
    except (ValueError, IndexError):
        await callback.answer("Invalid product", show_alert=True)
        return

    user_id = callback.from_user.id
    db.get_or_create_user(user_id, callback.from_user.username, callback.from_user.first_name)

    if db.is_in_wishlist(user_id, product_id):
        await callback.answer("Already in wishlist", show_alert=False)
        return

    db.add_to_wishlist(user_id, product_id)
    await callback.answer("Added to wishlist!", show_alert=False)


@router.callback_query(F.data.startswith("wishlist_del_"))
async def wishlist_del(callback: CallbackQuery):
    try:
        product_id = int(callback.data.split("_")[2])
    except (ValueError, IndexError):
        await callback.answer("Invalid item", show_alert=True)
        return

    user_id = callback.from_user.id
    db.remove_from_wishlist(user_id, product_id)
    await callback.answer("Removed from wishlist")

    await wishlist_view(callback)
