import asyncio
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from src.database import db

router = Router()

ORDER_SUMMARY_TEMPLATE = (
    "Order Summary\n\n"
    "{items}"
    "\nSubtotal: ${subtotal:.2f}\n"
    "{discount_line}"
    "Total: ${total:.2f}\n"
    "Your Balance: ${balance:.2f}\n\n"
    "Select Payment Method:"
)

PAYMENT_SUCCESS = (
    "Order Processed Successfully!\n\n"
    "{delivery_msg}"
    "New Balance: ${balance:.2f}\n"
)


class CouponStates(StatesGroup):
    waiting_for_code = State()


def get_checkout_keyboard(can_pay_credits: bool, has_coupon: bool = False) -> InlineKeyboardMarkup:
    buttons = []

    if can_pay_credits:
        buttons.append([InlineKeyboardButton(text="Pay with Balance", callback_data="pay_credits")])
    else:
        buttons.append([InlineKeyboardButton(text="Insufficient Balance (Topup)", callback_data="topup")])

    buttons.append([InlineKeyboardButton(text="Card / Crypto (Mock)", callback_data="pay_external")])

    if not has_coupon:
        buttons.append([InlineKeyboardButton(text="Apply Coupon", callback_data="apply_coupon")])

    buttons.append([InlineKeyboardButton(text="Cancel", callback_data="cart_view")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_order_complete_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="View Order History", callback_data="order_history")],
        [InlineKeyboardButton(text="Back to Home", callback_data="back_main")]
    ])


@router.callback_query(F.data == "checkout_start")
async def start_checkout(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user = db.get_or_create_user(user_id)
    cart = db.get_cart(user_id)

    if not cart:
        await callback.answer("Cart is empty!", show_alert=True)
        return

    subtotal = 0
    items_summary = ""

    for item in cart:
        product = item.get("products")
        if not product:
            continue

        qty = item["quantity"]
        stock = db.get_stock_count(product['id'])

        if stock < qty:
            await callback.answer(f"Not enough stock for {product['name']}!", show_alert=True)
            return

        item_total = float(product['price']) * qty
        subtotal += item_total
        items_summary += f"- {product['name']} (x{qty}) - ${item_total:.2f}\n"

    state_data = await state.get_data()
    coupon_code = state_data.get("coupon_code")
    discount = 0
    discount_line = ""

    if coupon_code:
        coupon, error = db.validate_coupon(coupon_code, subtotal)
        if coupon:
            discount = db.calculate_discount(coupon, subtotal)
            discount_line = f"Discount ({coupon_code}): -${discount:.2f}\n"

    total = subtotal - discount
    balance = float(user.get("balance", 0.0))
    can_pay_credits = balance >= total

    text = ORDER_SUMMARY_TEMPLATE.format(
        items=items_summary,
        subtotal=subtotal,
        discount_line=discount_line,
        total=total,
        balance=balance
    )

    keyboard = get_checkout_keyboard(can_pay_credits, bool(coupon_code))

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "apply_coupon")
async def apply_coupon_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CouponStates.waiting_for_code)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Cancel", callback_data="checkout_start")]
    ])
    await callback.message.edit_text("Enter your coupon code:", reply_markup=keyboard)
    await callback.answer()


@router.message(CouponStates.waiting_for_code)
async def process_coupon(message: Message, state: FSMContext):
    code = message.text.strip().upper()
    user_id = message.from_user.id
    cart_total = db.get_cart_total(user_id)

    coupon, error = db.validate_coupon(code, cart_total)

    if error:
        await message.answer(f"Invalid coupon: {error}")
        await state.clear()
        return

    discount = db.calculate_discount(coupon, cart_total)
    await state.update_data(coupon_code=code)
    await state.set_state(None)

    await message.answer(f"Coupon applied! Discount: ${discount:.2f}")

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Continue to Checkout", callback_data="checkout_start")]
    ])
    await message.answer("Click below to continue:", reply_markup=keyboard)


@router.callback_query(F.data == "pay_credits")
async def process_payment_credits(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user = db.get_user(user_id)
    cart = db.get_cart(user_id)

    if not cart:
        await callback.answer("Cart expired", show_alert=True)
        return

    subtotal = 0
    purchased_items = []

    for item in cart:
        product = item.get("products")
        if not product:
            continue
        qty = item["quantity"]
        subtotal += float(product['price']) * qty
        purchased_items.append({"product": product, "qty": qty, "product_id": product["id"]})

    state_data = await state.get_data()
    coupon_code = state_data.get("coupon_code")
    discount = 0

    if coupon_code:
        coupon, _ = db.validate_coupon(coupon_code, subtotal)
        if coupon:
            discount = db.calculate_discount(coupon, subtotal)

    total = subtotal - discount
    balance = float(user['balance'])

    if balance < total:
        await callback.answer("Insufficient balance!", show_alert=True)
        return

    for item in purchased_items:
        stock = db.get_stock_count(item['product_id'])
        if stock < item['qty']:
            await callback.answer(f"Insufficient stock for {item['product']['name']}!", show_alert=True)
            return

    order = db.create_order(user_id, total, discount, coupon_code, "balance")

    delivery_msg = ""

    for item in purchased_items:
        prod = item['product']
        qty = item['qty']

        stock_items = db.get_available_stock(prod['id'], qty)

        if stock_items:
            stock_ids = [s['id'] for s in stock_items]
            db.mark_stock_sold(stock_ids, user_id)

            delivery_msg += f"{prod['name']}\n"
            for s in stock_items:
                formatted = db.format_delivery_item(prod, s['data'])
                delivery_msg += f"{formatted}\n"
                db.add_order_item(order['id'], prod['id'], s['id'], float(prod['price']))
        else:
            delivery_msg += f"{prod['name']}\n"
            delivery_msg += "Auto-delivery failed (Contact Support)\n"

        delivery_msg += "\n"

    db.deduct_balance(user_id, total, f"Purchase - Order #{order['id']}")

    new_total_spent = float(user['total_spent']) + total
    db.update_user(user_id, {"total_spent": new_total_spent})
    db.update_user_tier(user_id)

    db.process_referral_commission(user_id, total)

    if coupon_code:
        db.use_coupon(coupon_code)

    db.clear_cart(user_id)
    await state.clear()

    new_user = db.get_user(user_id)
    new_balance = float(new_user['balance'])

    text = PAYMENT_SUCCESS.format(delivery_msg=delivery_msg, balance=new_balance)
    keyboard = get_order_complete_keyboard()

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer("Order Complete!")


@router.callback_query(F.data == "pay_external")
async def process_payment_mock(callback: CallbackQuery, state: FSMContext):
    await callback.answer("Processing Mock Payment...", show_alert=False)
    await asyncio.sleep(1)

    user_id = callback.from_user.id
    user = db.get_user(user_id)
    cart = db.get_cart(user_id)

    if not cart:
        await callback.answer("Cart expired", show_alert=True)
        return

    subtotal = 0
    purchased_items = []

    for item in cart:
        product = item.get("products")
        if not product:
            continue
        qty = item["quantity"]
        subtotal += float(product['price']) * qty
        purchased_items.append({"product": product, "qty": qty, "product_id": product["id"]})

    state_data = await state.get_data()
    coupon_code = state_data.get("coupon_code")
    discount = 0

    if coupon_code:
        coupon, _ = db.validate_coupon(coupon_code, subtotal)
        if coupon:
            discount = db.calculate_discount(coupon, subtotal)

    total = subtotal - discount

    for item in purchased_items:
        stock = db.get_stock_count(item['product_id'])
        if stock < item['qty']:
            await callback.answer(f"Insufficient stock for {item['product']['name']}!", show_alert=True)
            return

    order = db.create_order(user_id, total, discount, coupon_code, "external")

    delivery_msg = ""

    for item in purchased_items:
        prod = item['product']
        qty = item['qty']

        stock_items = db.get_available_stock(prod['id'], qty)

        if stock_items:
            stock_ids = [s['id'] for s in stock_items]
            db.mark_stock_sold(stock_ids, user_id)

            delivery_msg += f"{prod['name']}\n"
            for s in stock_items:
                formatted = db.format_delivery_item(prod, s['data'])
                delivery_msg += f"{formatted}\n"
                db.add_order_item(order['id'], prod['id'], s['id'], float(prod['price']))
        else:
            delivery_msg += f"{prod['name']}\n"
            delivery_msg += "Auto-delivery failed (Contact Support)\n"

        delivery_msg += "\n"

    new_total_spent = float(user['total_spent']) + total
    db.update_user(user_id, {"total_spent": new_total_spent})
    db.update_user_tier(user_id)

    db.process_referral_commission(user_id, total)

    if coupon_code:
        db.use_coupon(coupon_code)

    db.clear_cart(user_id)
    await state.clear()

    text = f"Payment Received!\n\n{delivery_msg}"
    keyboard = get_order_complete_keyboard()

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
