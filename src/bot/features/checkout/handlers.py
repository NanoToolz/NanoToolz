"""
Checkout feature - payment and order creation
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.orm import Session

from src.database import get_db
from src.database.models import User, CartItem, Product, Order, ProductDelivery
from src.logger import logger

router = Router()

@router.callback_query(F.data == "checkout_start")
async def start_checkout(callback: CallbackQuery):
    """Start checkout process"""
    db: Session = next(get_db())
    
    user = db.query(User).filter(User.telegram_id == callback.from_user.id).first()
    if not user:
        await callback.answer("User not found", show_alert=True)
        db.close()
        return
    
    cart_items = db.query(CartItem).filter(CartItem.user_id == user.id).all()
    
    if not cart_items:
        await callback.answer("Cart is empty!", show_alert=True)
        db.close()
        return
    
    # Calculate total
    total = 0
    for item in cart_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product:
            total += float(product.price_usd) * item.quantity
    
    # Show payment methods
    text = (
        f"💳 Checkout Summary\n\n"
        f"Items: {len(cart_items)}\n"
        f"Total: ${total:.2f}\n\n"
        f"Select a payment method:"
    )
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💳 Card (Simulated)", callback_data="pay_card")],
            [InlineKeyboardButton(text="💰 Credits", callback_data="pay_credits")],
            [InlineKeyboardButton(text="⬅️ Cancel", callback_data="cart_view")]
        ]
    )
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()
    db.close()

@router.callback_query(F.data == "pay_card")
async def pay_with_card(callback: CallbackQuery):
    """Payment with card (simulated)"""
    db: Session = next(get_db())
    
    user = db.query(User).filter(User.telegram_id == callback.from_user.id).first()
    if not user:
        await callback.answer("User not found", show_alert=True)
        db.close()
        return
    
    cart_items = db.query(CartItem).filter(CartItem.user_id == user.id).all()
    
    if not cart_items:
        await callback.answer("Cart is empty!", show_alert=True)
        db.close()
        return
    
    # Create orders from cart items
    try:
        delivery_messages = []
        for item in cart_items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                delivery_text = None
                delivery_items = (
                    db.query(ProductDelivery)
                    .filter(ProductDelivery.product_id == product.id, ProductDelivery.used == False)
                    .limit(item.quantity)
                    .all()
                )
                if delivery_items:
                    for delivery_item in delivery_items:
                        delivery_item.used = True
                    delivery_text = "\n".join([d.delivery_content for d in delivery_items])
                    delivery_messages.append(
                        f"📦 {product.name}\n{delivery_text}"
                    )

                order = Order(
                    user_id=user.id,
                    product_id=product.id,
                    quantity=item.quantity,
                    price_paid_usd=float(product.price_usd) * item.quantity,
                    price_paid_usdt=float(product.price_usdt) * item.quantity if product.price_usdt else 0,
                    payment_method="card",
                    payment_status="completed",
                    delivery_status="delivered" if delivery_text else "pending"
                )
                db.add(order)
                product.sales_count += item.quantity
        
        # Clear cart
        for item in cart_items:
            db.delete(item)
        
        db.commit()
        
        delivery_block = "\n\n".join(delivery_messages) if delivery_messages else ""
        text = (
            "✅ Payment Successful!\n\n"
            "Your order has been confirmed.\n"
            "You will receive your items shortly.\n\n"
            "Thank you for your purchase! 🎉"
        )

        if delivery_block:
            text += f"\n\n🎁 Delivery:\n{delivery_block}"
        
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🏠 Back to Home", callback_data="back_main")]
            ]
        )
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer("Order created successfully!", show_alert=False)
        logger.info(f"Order completed for user {user.telegram_id}")
        
    except Exception as e:
        logger.error(f"Checkout error: {e}")
        await callback.answer("Error processing order", show_alert=True)
    
    db.close()

@router.callback_query(F.data == "pay_credits")
async def pay_with_credits(callback: CallbackQuery):
    """Payment with account credits"""
    db: Session = next(get_db())
    
    user = db.query(User).filter(User.telegram_id == callback.from_user.id).first()
    if not user:
        await callback.answer("User not found", show_alert=True)
        db.close()
        return
    
    cart_items = db.query(CartItem).filter(CartItem.user_id == user.id).all()
    
    if not cart_items:
        await callback.answer("Cart is empty!", show_alert=True)
        db.close()
        return
    
    # Calculate total
    total = 0
    for item in cart_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product:
            total += float(product.price_usd) * item.quantity
    
    # Check if user has enough credits
    if float(user.credits) < total:
        needed = total - float(user.credits)
        text = (
            f"❌ Insufficient Credits\n\n"
            f"Your Balance: ${user.credits:.2f}\n"
            f"Need: ${total:.2f}\n"
            f"Missing: ${needed:.2f}"
        )
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="⬅️ Try Another Method", callback_data="checkout_start")]
            ]
        )
        await callback.message.edit_text(text, reply_markup=keyboard)
        db.close()
        return
    
    # Process payment
    try:
        delivery_messages = []
        for item in cart_items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                delivery_text = None
                delivery_items = (
                    db.query(ProductDelivery)
                    .filter(ProductDelivery.product_id == product.id, ProductDelivery.used == False)
                    .limit(item.quantity)
                    .all()
                )
                if delivery_items:
                    for delivery_item in delivery_items:
                        delivery_item.used = True
                    delivery_text = "\n".join([d.delivery_content for d in delivery_items])
                    delivery_messages.append(
                        f"📦 {product.name}\n{delivery_text}"
                    )

                order = Order(
                    user_id=user.id,
                    product_id=product.id,
                    quantity=item.quantity,
                    price_paid_usd=float(product.price_usd) * item.quantity,
                    price_paid_usdt=0,
                    credits_used=float(product.price_usd) * item.quantity,
                    payment_method="credits",
                    payment_status="completed",
                    delivery_status="delivered" if delivery_text else "pending"
                )
                db.add(order)
                product.sales_count += item.quantity
        
        # Deduct credits
        user.credits -= total
        
        # Clear cart
        for item in cart_items:
            db.delete(item)
        
        db.commit()
        
        delivery_block = "\n\n".join(delivery_messages) if delivery_messages else ""
        text = (
            "✅ Payment Successful!\n\n"
            f"Credits Used: ${total:.2f}\n"
            f"New Balance: ${user.credits:.2f}\n\n"
            "Your order has been confirmed."
        )

        if delivery_block:
            text += f"\n\n🎁 Delivery:\n{delivery_block}"
        
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🏠 Back to Home", callback_data="back_main")]
            ]
        )
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer("Order created successfully!", show_alert=False)
        logger.info(f"Order completed with credits for user {user.telegram_id}")
        
    except Exception as e:
        logger.error(f"Checkout error: {e}")
        await callback.answer("Error processing order", show_alert=True)
    
    db.close()