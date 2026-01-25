from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from src.database.json_db import db
from src.logger import logger

router = Router()

@router.callback_query(F.data.startswith("add_cart_"))
async def add_to_cart(callback: CallbackQuery):
    prod_id = int(callback.data.split("_")[2])
    user_id = callback.from_user.id
    
    user = db.get_user(user_id)
    cart = user.get("cart", {})
    
    # Check if stock available
    if db.get_stock_count(prod_id) <= 0:
        await callback.answer("❌ Out of Stock!", show_alert=True)
        return

    # Add to cart dict: product_id -> qty
    pid_str = str(prod_id)
    current_qty = cart.get(pid_str, 0)
    cart[pid_str] = current_qty + 1
    
    db.update_user(user_id, {"cart": cart})
    
    await callback.answer("✅ Added to cart!", show_alert=False)
    # logger.info(f"User {user_id} added product {prod_id} to cart")

@router.callback_query(F.data == "cart_view")
async def view_cart(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = db.get_user(user_id)
    cart = user.get("cart", {})
    
    if not cart:
        text = "🛒 **Your Cart is Empty**\n\nBrowse our catalog to add items."
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🛍️ Browse Catalog", callback_data="catalog_main")],
                [InlineKeyboardButton(text="⬅️ Back", callback_data="back_main")]
            ]
        )
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
        await callback.answer()
        return

    total_price = 0
    text = "🛒 **Your Shopping Cart**\n\n"
    buttons = []
    
    for pid_str, qty in cart.items():
        product = db.get_product(int(pid_str))
        if not product:
            continue
            
        subtotal = product['price'] * qty
        total_price += subtotal
        text += f"▪️ **{product['name']}**\n   {qty} x ${product['price']} = ${subtotal:.2f}\n"
        
        # Quantity controls
        buttons.append([
            InlineKeyboardButton(text=f"➖", callback_data=f"cart_dec_{pid_str}"),
            InlineKeyboardButton(text=f"{qty}", callback_data="noop"),
            InlineKeyboardButton(text=f"➕", callback_data=f"cart_inc_{pid_str}"),
            InlineKeyboardButton(text=f"🗑️", callback_data=f"cart_rem_{pid_str}")
        ])
        
    text += f"\n💰 **Total: ${total_price:.2f}**"
    
    buttons.append([InlineKeyboardButton(text="✅ Checkout", callback_data="checkout_start")])
    buttons.append([InlineKeyboardButton(text="⬅️ Back", callback_data="back_main")])
    
    await callback.message.edit_text(
        text, 
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("cart_inc_"))
async def increase_cart_item(callback: CallbackQuery):
    pid_str = callback.data.split("_")[2]
    user_id = callback.from_user.id
    user = db.get_user(user_id)
    cart = user.get("cart", {})
    
    if pid_str in cart:
        cart[pid_str] += 1
        db.update_user(user_id, {"cart": cart})
        
    await view_cart(callback)

@router.callback_query(F.data.startswith("cart_dec_"))
async def decrease_cart_item(callback: CallbackQuery):
    pid_str = callback.data.split("_")[2]
    user_id = callback.from_user.id
    user = db.get_user(user_id)
    cart = user.get("cart", {})
    
    if pid_str in cart:
        if cart[pid_str] > 1:
            cart[pid_str] -= 1
        else:
            del cart[pid_str]
        db.update_user(user_id, {"cart": cart})
        
    await view_cart(callback)

@router.callback_query(F.data.startswith("cart_rem_"))
async def remove_cart_item(callback: CallbackQuery):
    pid_str = callback.data.split("_")[2]
    user_id = callback.from_user.id
    user = db.get_user(user_id)
    cart = user.get("cart", {})
    
    if pid_str in cart:
        del cart[pid_str]
        db.update_user(user_id, {"cart": cart})
        
    await view_cart(callback)
    await callback.answer("Item removed")