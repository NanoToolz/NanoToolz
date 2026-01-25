from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from src.database.json_db import db

router = Router()

@router.callback_query(F.data == "profile_view")
async def view_profile(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = db.get_user(user_id)
    
    # Calculate stats
    total_orders = len(user.get("orders", [])) # In reality we'd scan orders.json for user_id
    # Since orders.json is separate now, let's scan it
    user_orders = [o for o in db.orders if str(o.get('user_id')) == str(user_id)]
    
    text = (
        f"👤 **User Profile**\n\n"
        f"🆔 ID: `{user_id}`\n"
        f"👤 Name: {callback.from_user.full_name}\n"
        f"💰 Balance: **${user.get('balance', 0.0):.2f}**\n"
        f"📦 Total Orders: {len(user_orders)}\n"
        f"� Joined: {user.get('joined_at', 'Recently')}\n"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Topup Balance", callback_data="topup")],
        [InlineKeyboardButton(text="� Order History", callback_data="order_history")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="back_main")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "order_history")
async def view_order_history(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_orders = [o for o in db.orders if str(o.get('user_id')) == str(user_id)]
    
    if not user_orders:
        await callback.answer("No orders found", show_alert=True)
        return
        
    # Show last 5 orders
    recent = sorted(user_orders, key=lambda x: x.get('timestamp', 0), reverse=True)[:5]
    
    text = "📜 **Recent Orders**\n\n"
    for order in recent:
        prod = db.get_product(order['product_id'])
        prod_name = prod['name'] if prod else "Unknown Product"
        text += f"🔹 **{prod_name}**\n   Price: ${order.get('total', 0):.2f}\n   Keys: {len(order.get('keys_delivered', []))}\n\n"
        
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back to Profile", callback_data="profile_view")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")