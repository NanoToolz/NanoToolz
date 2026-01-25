# ============================================
# FEATURE: Checkout & Payment
# ============================================
# Purpose: Process payments and deliver orders
# Handles payment methods, order creation, and auto-delivery

# ===== IMPORTS =====
import asyncio
import time
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from src.database.json_db import db

router = Router()

# ============================================
# ===== MESSAGES SECTION =====
# ============================================

# Order summary template
ORDER_SUMMARY_TEMPLATE = (
    "📝 **Order Summary**\n\n"
    "{items}"
    "\n💰 Total: **${total:.2f}**\n"
    "💳 Your Balance: **${balance:.2f}**\n\n"
    "Select Payment Method:"
)

# Payment success message
PAYMENT_SUCCESS = (
    "✅ **Order Processed Successfully!**\n\n"
    "{delivery_msg}"
    "💰 New Balance: ${balance:.2f}\n"
)

# ============================================
# ===== KEYBOARDS SECTION =====
# ============================================

def get_checkout_keyboard(can_pay_credits: bool) -> InlineKeyboardMarkup:
    """
    Build payment method selection keyboard
    
    Args:
        can_pay_credits: Whether user has enough balance
    
    Returns:
        Keyboard with payment options
    """
    buttons = []
    
    # Add credit payment button if user has enough balance
    if can_pay_credits:
        buttons.append([InlineKeyboardButton(text="💰 Pay with Credits", callback_data="pay_credits")])
    else:
        # Show topup button if insufficient balance
        buttons.append([InlineKeyboardButton(text="⚠️ Insufficient Credits (Topup)", callback_data="topup")])
    
    # Add external payment option (Crypto/Card)
    buttons.append([InlineKeyboardButton(text="💳 Card / Crypto (Mock)", callback_data="pay_external")])
    
    # Add cancel button
    buttons.append([InlineKeyboardButton(text="❌ Cancel", callback_data="cart_view")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_order_complete_keyboard() -> InlineKeyboardMarkup:
    """
    Build keyboard after successful order
    
    Returns:
        Keyboard with home and shop buttons
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Back to Home", callback_data="back_main")]
    ])

# ============================================
# ===== HANDLERS SECTION =====
# ============================================

@router.callback_query(F.data == "checkout_start")
async def start_checkout(callback: CallbackQuery):
    """
    Start checkout process
    
    Shows order summary and payment method options
    """
    # Get user ID and data
    user_id = callback.from_user.id
    user = db.get_user(user_id)
    cart = user.get("cart", {})
    
    # Check if cart is empty
    if not cart:
        await callback.answer("Cart is empty!", show_alert=True)
        return
    
    # Calculate total and check stock
    total_price = 0
    items_summary = ""
    
    for pid_str, qty in cart.items():
        product = db.get_product(int(pid_str))
        if not product:
            continue
        
        # Check if enough stock available
        stock = db.get_stock_count(product['id'])
        if stock < qty:
            await callback.answer(f"⚠️ Not enough stock for {product['name']}!", show_alert=True)
            return
        
        # Add to total and summary
        total_price += product['price'] * qty
        items_summary += f"▪️ {product['name']} (x{qty})\n"
    
    # Get user's current balance
    balance = user.get("balance", 0.0)
    
    # Check if user can pay with credits
    can_pay_credits = balance >= total_price
    
    # Build order summary text
    text = ORDER_SUMMARY_TEMPLATE.format(
        items=items_summary,
        total=total_price,
        balance=balance
    )
    
    # Build payment method keyboard
    keyboard = get_checkout_keyboard(can_pay_credits)
    
    # Edit message to show checkout
    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    
    await callback.answer()

@router.callback_query(F.data == "pay_credits")
async def process_payment_credits(callback: CallbackQuery):
    """
    Process payment using account credits
    
    Deducts balance, delivers keys, and creates order record
    """
    # Get user and cart
    user_id = callback.from_user.id
    user = db.get_user(user_id)
    cart = user.get("cart", {})
    
    # Check if cart still exists
    if not cart:
        await callback.answer("Cart expired", show_alert=True)
        return
    
    # Recalculate total
    total_price = 0
    purchased_items = []
    
    for pid_str, qty in cart.items():
        product = db.get_product(int(pid_str))
        total_price += product['price'] * qty
        purchased_items.append({"product": product, "qty": qty})
    
    # Check if user has enough balance
    if user['balance'] < total_price:
        await callback.answer("Insufficient balance!", show_alert=True)
        return
    
    # Validate stock one more time
    for item in purchased_items:
        prod = item['product']
        stock = db.get_stock_count(prod['id'])
        if stock < item['qty']:
            await callback.answer(f"⚠️ Insufficient stock for {prod['name']}!", show_alert=True)
            return
    
    # Deduct balance from user account
    new_balance = user['balance'] - total_price
    
    # Process delivery for each item
    delivery_msg = ""
    
    for item in purchased_items:
        prod = item['product']
        qty = item['qty']
        
        # Get keys from stock
        keys = db.pop_stock(prod['id'], qty)
        
        # Build delivery message
        delivery_msg += f"📦 **{prod['name']}**\n"
        if keys:
            # Show each key
            for k in keys:
                delivery_msg += f"key: `{k}`\n"
        else:
            delivery_msg += "⚠️ Auto-delivery failed (Contact Support)\n"
        delivery_msg += "\n"
        
        # Create order record in database
        db.create_order({
            "user_id": user_id,
            "product_id": prod['id'],
            "qty": qty,
            "total": prod['price'] * qty,
            "keys_delivered": keys,
            "timestamp": time.time()
        })
    
    # Update user: clear cart and update balance
    db.update_user(user_id, {
        "balance": new_balance,
        "cart": {}
    })
    
    # Build success message
    text = PAYMENT_SUCCESS.format(
        delivery_msg=delivery_msg,
        balance=new_balance
    )
    
    # Show order complete message
    keyboard = get_order_complete_keyboard()
    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    
    await callback.answer("Order Complete!")

@router.callback_query(F.data == "pay_external")
async def process_payment_mock(callback: CallbackQuery):
    """
    Process mock external payment (Crypto/Card)
    
    For demo purposes - in production, integrate with payment gateway
    """
    # Show processing message
    await callback.answer("Processing Mock Payment...", show_alert=False)
    
    # Simulate payment processing delay
    await asyncio.sleep(1)
    
    # Get user and cart
    user_id = callback.from_user.id
    user = db.get_user(user_id)
    cart = user.get("cart", {})
    
    # Check if cart exists
    if not cart:
        await callback.answer("Cart expired", show_alert=True)
        return
    
    # Prepare items for delivery
    purchased_items = []
    total_price = 0
    
    for pid_str, qty in cart.items():
        product = db.get_product(int(pid_str))
        total_price += product['price'] * qty
        purchased_items.append({"product": product, "qty": qty})
    
    # Validate stock before processing
    for item in purchased_items:
        prod = item['product']
        qty = item['qty']
        stock = db.get_stock_count(prod['id'])
        if stock < qty:
            await callback.answer(f"⚠️ Insufficient stock for {prod['name']}!", show_alert=True)
            return
    
    # Process delivery
    delivery_msg = ""
    
    for item in purchased_items:
        prod = item['product']
        qty = item['qty']
        
        # Get keys from stock
        keys = db.pop_stock(prod['id'], qty)
        
        # Build delivery message
        delivery_msg += f"📦 **{prod['name']}**\n"
        if keys:
            for k in keys:
                delivery_msg += f"key: `{k}`\n"
        else:
            delivery_msg += "⚠️ Auto-delivery failed (Contact Support)\n"
        delivery_msg += "\n"
        
        # Create order record
        db.create_order({
            "user_id": user_id,
            "product_id": prod['id'],
            "qty": qty,
            "total": prod['price'] * qty,
            "keys_delivered": keys,
            "payment_method": "external",
            "timestamp": time.time()
        })
    
    # Clear cart (no balance deduction for external payment)
    db.update_user(user_id, {"cart": {}})
    
    # Show success message
    text = f"✅ **Payment Received!**\n\n{delivery_msg}"
    keyboard = get_order_complete_keyboard()
    
    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
