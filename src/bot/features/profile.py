# ============================================
# FEATURE: User Profile
# ============================================
# Purpose: Display user profile and order history
# Shows user stats, balance, and past orders

# ===== IMPORTS =====
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from src.database.json_db import db

router = Router()

# ============================================
# ===== MESSAGES SECTION =====
# ============================================

# Profile display template
PROFILE_TEMPLATE = (
    "👤 **User Profile**\n\n"
    "🆔 ID: `{user_id}`\n"
    "👤 Name: {full_name}\n"
    "💰 Balance: **${balance:.2f}**\n"
    "📦 Total Orders: {total_orders}\n"
    "📅 Joined: {joined_at}\n"
)

# Order history title
ORDER_HISTORY_TITLE = "📜 **Recent Orders**\n\n"

# Template for each order
ORDER_ITEM_TEMPLATE = "🔹 **{product_name}**\n   Price: ${total:.2f}\n   Keys: {keys_count}\n\n"

# ============================================
# ===== KEYBOARDS SECTION =====
# ============================================

def get_profile_keyboard() -> InlineKeyboardMarkup:
    """Build profile menu keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Topup Balance", callback_data="topup")],
        [InlineKeyboardButton(text="📜 Order History", callback_data="order_history")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="back_main")]
    ])

def get_order_history_keyboard() -> InlineKeyboardMarkup:
    """Build order history keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back to Profile", callback_data="profile_view")]
    ])

# ============================================
# ===== HANDLERS SECTION =====
# ============================================

@router.callback_query(F.data == "profile_view")
async def view_profile(callback: CallbackQuery):
    """
    Display user profile
    
    Shows user ID, name, balance, order count, and join date
    """
    # Get user ID
    user_id = callback.from_user.id
    
    # Get user data from database
    user = db.get_user(user_id)
    
    # Get all orders for this user
    user_orders = [o for o in db.orders if str(o.get('user_id')) == str(user_id)]
    
    # Build profile text
    text = PROFILE_TEMPLATE.format(
        user_id=user_id,
        full_name=callback.from_user.full_name,
        balance=user.get('balance', 0.0),
        total_orders=len(user_orders),
        joined_at=user.get('joined_at', 'Recently')
    )
    
    # Build keyboard
    keyboard = get_profile_keyboard()
    
    # Edit message to show profile
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "order_history")
async def view_order_history(callback: CallbackQuery):
    """
    Display user's order history
    
    Shows last 5 orders with product names and prices
    """
    # Get user ID
    user_id = callback.from_user.id
    
    # Get all orders for this user
    user_orders = [o for o in db.orders if str(o.get('user_id')) == str(user_id)]
    
    # Check if user has any orders
    if not user_orders:
        await callback.answer("No orders found", show_alert=True)
        return
    
    # Sort by timestamp (newest first) and get last 5
    recent = sorted(user_orders, key=lambda x: x.get('timestamp', 0), reverse=True)[:5]
    
    # Build order history text
    text = ORDER_HISTORY_TITLE
    for order in recent:
        # Get product details
        prod = db.get_product(order['product_id'])
        prod_name = prod['name'] if prod else "Unknown Product"
        
        # Add order to text
        text += ORDER_ITEM_TEMPLATE.format(
            product_name=prod_name,
            total=order.get('total', 0),
            keys_count=len(order.get('keys_delivered', []))
        )
    
    # Build keyboard
    keyboard = get_order_history_keyboard()
    
    # Edit message to show order history
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()
