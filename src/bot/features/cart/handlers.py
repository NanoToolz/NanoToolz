"""
Cart feature - manage shopping cart
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.orm import Session

from src.database import get_db
from src.database.models import User, CartItem, Product
from src.logger import logger

router = Router()

@router.callback_query(F.data == "cart_view")
async def view_cart(callback: CallbackQuery):
    """View shopping cart"""
    db: Session = next(get_db())
    
    user = db.query(User).filter(User.telegram_id == callback.from_user.id).first()
    if not user:
        await callback.answer("User not found", show_alert=True)
        db.close()
        return
    
    cart_items = db.query(CartItem).filter(CartItem.user_id == user.id).all()
    
    if not cart_items:
        text = "🛒 Your cart is empty!\n\nBrowse our catalog to add items."
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🛍️ Browse Catalog", callback_data="catalog_main")],
                [InlineKeyboardButton(text="⬅️ Back", callback_data="back_main")]
            ]
        )
        await callback.message.edit_text(text, reply_markup=keyboard)
        db.close()
        return
    
    # Build cart display
    total = 0
    cart_text = "🛒 Your Cart:\n\n"
    buttons = []
    
    for item in cart_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product:
            subtotal = float(product.price_usd) * item.quantity
            total += subtotal
            cart_text += f"📦 {product.name}\n  Qty: {item.quantity} x ${product.price_usd} = ${subtotal:.2f}\n\n"
            buttons.append([
                InlineKeyboardButton(text=f"➖ {product.name}", callback_data=f"rem_{item.id}"),
                InlineKeyboardButton(text=f"✏️ {item.quantity}", callback_data=f"upd_{item.id}")
            ])
    
    cart_text += f"\n💰 Total: ${total:.2f}"
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=buttons + [
            [InlineKeyboardButton(text="🛒 Continue Shopping", callback_data="catalog_main")],
            [InlineKeyboardButton(text="✅ Checkout", callback_data="checkout_start")],
            [InlineKeyboardButton(text="⬅️ Back", callback_data="back_main")]
        ]
    )
    
    await callback.message.edit_text(cart_text, reply_markup=keyboard)
    await callback.answer()
    db.close()

@router.callback_query(F.data.startswith("rem_"))
async def remove_from_cart(callback: CallbackQuery):
    """Remove item from cart"""
    db: Session = next(get_db())
    
    item_id = int(callback.data.split("_")[1])
    cart_item = db.query(CartItem).filter(CartItem.id == item_id).first()
    
    if cart_item:
        db.delete(cart_item)
        db.commit()
        await callback.answer("✅ Item removed", show_alert=False)
        logger.info(f"Item {item_id} removed from cart")
    else:
        await callback.answer("Item not found", show_alert=True)
    
    # Refresh cart view
    await view_cart(callback)
    db.close()

@router.callback_query(F.data.startswith("upd_"))
async def update_quantity(callback: CallbackQuery):
    """Cycle through quantity options"""
    db: Session = next(get_db())
    
    item_id = int(callback.data.split("_")[1])
    cart_item = db.query(CartItem).filter(CartItem.id == item_id).first()
    
    if cart_item:
        # Cycle: 1 -> 2 -> 3 -> 5 -> 10 -> 1
        qty_options = [1, 2, 3, 5, 10]
        current_idx = qty_options.index(cart_item.quantity) if cart_item.quantity in qty_options else 0
        next_idx = (current_idx + 1) % len(qty_options)
        cart_item.quantity = qty_options[next_idx]
        db.commit()
        await callback.answer(f"Qty: {cart_item.quantity}", show_alert=False)
    
    # Refresh cart
    await view_cart(callback)
    db.close()

@router.callback_query(F.data == "back_main")
async def back_to_main(callback: CallbackQuery):
    """Go back to main menu"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🛍️ Browse Catalog", callback_data="catalog_main")],
            [InlineKeyboardButton(text="🛒 View Cart", callback_data="cart_view")],
            [InlineKeyboardButton(text="� Topup", callback_data="topup")],
            [InlineKeyboardButton(text="🎁 Daily Spin", callback_data="daily_spin")],
            [InlineKeyboardButton(text="�👤 Profile", callback_data="profile_view")],
            [InlineKeyboardButton(text="📞 Support", callback_data="support")],
            [InlineKeyboardButton(text="❓ Help", callback_data="help_main")],
            [InlineKeyboardButton(text="🔐 Admin Panel", callback_data="admin_panel")]
        ]
    )
    
    await callback.message.edit_text("Main Menu - What would you like to do?", reply_markup=keyboard)
    await callback.answer()