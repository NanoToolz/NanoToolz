import asyncio
import time
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from src.database.json_db import db

router = Router()

@router.callback_query(F.data == "checkout_start")
async def start_checkout(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = db.get_user(user_id)
    cart = user.get("cart", {})
    
    if not cart:
        await callback.answer("Cart is empty!", show_alert=True)
        return
        
    total_price = 0
    items_summary = ""
    
    # Calculate total & check stock
    for pid_str, qty in cart.items():
        product = db.get_product(int(pid_str))
        if not product:
            continue
            
        stock = db.get_stock_count(product['id'])
        if stock < qty:
            await callback.answer(f"⚠️ Not enough stock for {product['name']}!", show_alert=True)
            return
            
        total_price += product['price'] * qty
        items_summary += f"▪️ {product['name']} (x{qty})\n"
        
    # Check User Balance
    balance = user.get("balance", 0.0)
    can_pay_credits = balance >= total_price
    
    text = (
        f"📝 **Order Summary**\n\n"
        f"{items_summary}\n"
        f"💰 Total: **${total_price:.2f}**\n"
        f"💳 Your Balance: **${balance:.2f}**\n\n"
        "Select Payment Method:"
    )
    
    buttons = []
    if can_pay_credits:
        buttons.append([InlineKeyboardButton(text="💰 Pay with Credits", callback_data="pay_credits")])
    else:
        buttons.append([InlineKeyboardButton(text="⚠️ Insufficient Credits (Topup)", callback_data="topup")])
        
    # Placeholder for crypto/external (mock)
    buttons.append([InlineKeyboardButton(text="💳 Card / Crypto (Mock)", callback_data="pay_external")])
    buttons.append([InlineKeyboardButton(text="❌ Cancel", callback_data="cart_view")])
    
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "pay_credits")
async def process_payment_credits(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = db.get_user(user_id)
    cart = user.get("cart", {})
    
    if not cart:
        await callback.answer("Cart expired", show_alert=True)
        return

    # Re-calculate total
    total_price = 0
    purchased_items = []
    
    for pid_str, qty in cart.items():
        product = db.get_product(int(pid_str))
        total_price += product['price'] * qty
        purchased_items.append({"product": product, "qty": qty})
        
    if user['balance'] < total_price:
        await callback.answer("Insufficient balance!", show_alert=True)
        return

    # Validate stock again after lock acquisition
    for item in purchased_items:
        prod = item['product']
        stock = db.get_stock_count(prod['id'])
        if stock < item['qty']:
            await callback.answer(f"⚠️ Insufficient stock for {prod['name']}!", show_alert=True)
            return

    # Deduct Balance
    new_balance = user['balance'] - total_price
    
    # Process Delivery
    delivery_msg = "✅ **Order Processed Successfully!**\n\n"
    
    for item in purchased_items:
        prod = item['product']
        qty = item['qty']
        
        # Get Keys
        keys = db.pop_stock(prod['id'], qty)
        
        delivery_msg += f"📦 **{prod['name']}**\n"
        if keys:
            for k in keys:
                delivery_msg += f"key: `{k}`\n"
        else:
            delivery_msg += "⚠️ Auto-delivery failed (Contact Support)\n"
        delivery_msg += "\n"
        
        # Record Order
        db.create_order({
            "user_id": user_id,
            "product_id": prod['id'],
            "qty": qty,
            "total": prod['price'] * qty,
            "keys_delivered": keys,
            "timestamp": time.time()
        })
    
    # Clear Cart & Save User
    db.update_user(user_id, {
        "balance": new_balance,
        "cart": {}
    })
    
    delivery_msg += f"💰 New Balance: ${new_balance:.2f}\n"
    
    # Send Delivery
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Back to Home", callback_data="back_main")]
    ])
    
    await callback.message.edit_text(
        delivery_msg,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer("Order Complete!")

@router.callback_query(F.data == "pay_external")
async def process_payment_mock(callback: CallbackQuery):
    # Mock external payment success
    await callback.answer("Processing Mock Payment...", show_alert=False)
    await asyncio.sleep(1) # Fake delay
    
    # Since it's external, we don't deduct credits, but we do everything else.
    # In real app, this would be a webhook callback.
    user_id = callback.from_user.id
    user = db.get_user(user_id)
    cart = user.get("cart", {})
    
    purchased_items = []
    total_price = 0
    for pid_str, qty in cart.items():
        product = db.get_product(int(pid_str))
        total_price += product['price'] * qty
        purchased_items.append({"product": product, "qty": qty})
        
    # Validate stock again before processing
    for item in purchased_items:
        prod = item['product']
        qty = item['qty']
        stock = db.get_stock_count(prod['id'])
        if stock < qty:
            await callback.answer(f"⚠️ Insufficient stock for {prod['name']}!", show_alert=True)
            return
    
    delivery_msg = "✅ **Payment Received!**\n\n"
    
    for item in purchased_items:
        prod = item['product']
        qty = item['qty']
        keys = db.pop_stock(prod['id'], qty)
        
        delivery_msg += f"📦 **{prod['name']}**\n"
        if keys:
            for k in keys:
                delivery_msg += f"key: `{k}`\n"
        else:
            delivery_msg += "⚠️ Auto-delivery failed (Contact Support)\n"
        delivery_msg += "\n"
        
        db.create_order({
            "user_id": user_id,
            "product_id": prod['id'],
            "qty": qty,
            "total": prod['price'] * qty,
            "keys_delivered": keys,
            "payment_method": "external",
            "timestamp": time.time()
        })
        
    db.update_user(user_id, {"cart": {}})
    
    await callback.message.edit_text(
        delivery_msg,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🏠 Home", callback_data="back_main")]]),
        parse_mode="Markdown"
    )