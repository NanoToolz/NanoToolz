"""
Profile feature - user account management
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.orm import Session

from src.database import get_db
from src.database.models import User, Order

router = Router()

@router.callback_query(F.data == "profile_view")
async def view_profile(callback: CallbackQuery):
    """View user profile"""
    db: Session = next(get_db())
    
    user = db.query(User).filter(User.telegram_id == callback.from_user.id).first()
    if not user:
        await callback.answer("User not found", show_alert=True)
        db.close()
        return
    
    # Count orders
    orders_count = db.query(Order).filter(Order.user_id == user.id).count()
    
    text = (
        f"👤 Your Profile\n\n"
        f"Name: {user.first_name or 'N/A'}\n"
        f"Username: @{user.username or 'N/A'}\n"
        f"ID: {user.telegram_id}\n\n"
        f"💰 Account Balance: ${user.credits:.2f}\n"
        f"📦 Orders: {orders_count}\n"
        f"🌍 Currency: {user.currency}\n"
        f"🗣️ Language: {user.language}\n\n"
        f"Joined: {user.created_at.strftime('%Y-%m-%d')}"
    )
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📋 Order History", callback_data="profile_orders")],
            [InlineKeyboardButton(text="⬅️ Back", callback_data="back_main")]
        ]
    )
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()
    db.close()

@router.callback_query(F.data == "profile_orders")
async def view_orders(callback: CallbackQuery):
    """View order history"""
    db: Session = next(get_db())
    
    user = db.query(User).filter(User.telegram_id == callback.from_user.id).first()
    if not user:
        await callback.answer("User not found", show_alert=True)
        db.close()
        return
    
    orders = db.query(Order).filter(Order.user_id == user.id).all()
    
    if not orders:
        text = "📦 Order History\n\nYou have no orders yet."
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🛍️ Start Shopping", callback_data="catalog_main")],
                [InlineKeyboardButton(text="⬅️ Back", callback_data="profile_view")]
            ]
        )
        await callback.message.edit_text(text, reply_markup=keyboard)
        db.close()
        return
    
    text = "📦 Order History\n\n"
    for i, order in enumerate(orders[-5:], 1):  # Last 5 orders
        from src.database.models import Product
        product = db.query(Product).filter(Product.id == order.product_id).first()
        status_emoji = "✅" if order.payment_status == "completed" else "⏳"
        text += (
            f"{i}. {product.name if product else 'N/A'}\n"
            f"   {status_emoji} ${order.price_paid_usd} | {order.created_at.strftime('%Y-%m-%d')}\n\n"
        )
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Back", callback_data="profile_view")]
        ]
    )
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()
    db.close()