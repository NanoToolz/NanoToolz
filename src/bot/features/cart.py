from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from src.database import db

router = Router()

EMPTY_CART = "Your Cart is Empty\n\nBrowse our catalog to add items."
CART_TITLE = "Your Shopping Cart\n\n"
CART_ITEM_TEMPLATE = "- {name}\n   {qty} x ${price} = ${subtotal:.2f}\n"
CART_TOTAL = "\nTotal: ${total:.2f}"


def get_empty_cart_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Browse Catalog", callback_data="catalog_main")],
            [InlineKeyboardButton(text="Back", callback_data="back_main")]
        ]
    )


def get_cart_keyboard(cart_items: list) -> InlineKeyboardMarkup:
    buttons = []

    for item in cart_items:
        prod_id = item["product_id"]
        qty = item["quantity"]
        buttons.append([
            InlineKeyboardButton(text="-", callback_data=f"cart_dec_{prod_id}"),
            InlineKeyboardButton(text=f"{qty}", callback_data="noop"),
            InlineKeyboardButton(text="+", callback_data=f"cart_inc_{prod_id}"),
            InlineKeyboardButton(text="X", callback_data=f"cart_rem_{prod_id}")
        ])

    buttons.append([InlineKeyboardButton(text="Apply Coupon", callback_data="apply_coupon")])
    buttons.append([InlineKeyboardButton(text="Checkout", callback_data="checkout_start")])
    buttons.append([InlineKeyboardButton(text="Back", callback_data="back_main")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.callback_query(F.data == "cart_view")
async def view_cart(callback: CallbackQuery):
    user_id = callback.from_user.id
    db.get_or_create_user(user_id)

    cart = db.get_cart(user_id)

    if not cart:
        keyboard = get_empty_cart_keyboard()
        try:
            await callback.message.edit_text(EMPTY_CART, reply_markup=keyboard, parse_mode="Markdown")
        except Exception:
            await callback.message.delete()
            await callback.message.answer(EMPTY_CART, reply_markup=keyboard, parse_mode="Markdown")
        await callback.answer()
        return

    total_price = 0
    text = CART_TITLE

    for item in cart:
        product = item.get("products")
        if not product:
            continue

        qty = item["quantity"]
        price = float(product["price"])
        subtotal = price * qty
        total_price += subtotal

        text += CART_ITEM_TEMPLATE.format(
            name=product['name'],
            qty=qty,
            price=price,
            subtotal=subtotal
        )

    text += CART_TOTAL.format(total=total_price)

    keyboard = get_cart_keyboard(cart)

    try:
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    except Exception:
        await callback.message.delete()
        await callback.message.answer(text, reply_markup=keyboard, parse_mode="Markdown")

    await callback.answer()


@router.callback_query(F.data.startswith("cart_inc_"))
async def increase_cart_item(callback: CallbackQuery):
    try:
        prod_id = int(callback.data.split("_")[2])
    except (ValueError, IndexError):
        await callback.answer("Invalid product", show_alert=True)
        return

    user_id = callback.from_user.id

    stock = db.get_stock_count(prod_id)
    cart = db.get_cart(user_id)
    current_qty = 0
    for item in cart:
        if item["product_id"] == prod_id:
            current_qty = item["quantity"]
            break

    if current_qty >= stock:
        await callback.answer("Not enough stock available", show_alert=True)
        return

    db.add_to_cart(user_id, prod_id, 1)
    await view_cart(callback)


@router.callback_query(F.data.startswith("cart_dec_"))
async def decrease_cart_item(callback: CallbackQuery):
    try:
        prod_id = int(callback.data.split("_")[2])
    except (ValueError, IndexError):
        await callback.answer("Invalid product", show_alert=True)
        return

    user_id = callback.from_user.id

    cart = db.get_cart(user_id)
    current_qty = 0
    for item in cart:
        if item["product_id"] == prod_id:
            current_qty = item["quantity"]
            break

    if current_qty <= 1:
        db.remove_from_cart(user_id, prod_id)
    else:
        db.update_cart_quantity(user_id, prod_id, current_qty - 1)

    await view_cart(callback)


@router.callback_query(F.data.startswith("cart_rem_"))
async def remove_cart_item(callback: CallbackQuery):
    try:
        prod_id = int(callback.data.split("_")[2])
    except (ValueError, IndexError):
        await callback.answer("Invalid product", show_alert=True)
        return

    user_id = callback.from_user.id
    db.remove_from_cart(user_id, prod_id)

    await callback.answer("Item removed")
    await view_cart(callback)


@router.callback_query(F.data.startswith("add_cart_"))
async def add_to_cart(callback: CallbackQuery):
    try:
        prod_id = int(callback.data.split("_")[2])
    except (IndexError, ValueError):
        await callback.answer("Invalid product!", show_alert=True)
        return

    user_id = callback.from_user.id
    db.get_or_create_user(user_id, callback.from_user.username, callback.from_user.first_name)

    stock = db.get_stock_count(prod_id)
    if stock <= 0:
        await callback.answer("Out of Stock!", show_alert=True)
        return

    cart = db.get_cart(user_id)
    current_qty = 0
    for item in cart:
        if item["product_id"] == prod_id:
            current_qty = item["quantity"]
            break

    if current_qty >= stock:
        await callback.answer("Cannot add more - not enough stock", show_alert=True)
        return

    db.add_to_cart(user_id, prod_id, 1)
    await callback.answer("Added to cart!", show_alert=False)


@router.callback_query(F.data == "noop")
async def noop_handler(callback: CallbackQuery):
    await callback.answer()
