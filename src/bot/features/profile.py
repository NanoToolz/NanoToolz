from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from src.database import db

router = Router()

TIER_EMOJI = {"bronze": "", "silver": "", "gold": "", "platinum": ""}

PROFILE_TEMPLATE = (
    "User Profile\n\n"
    "ID: `{user_id}`\n"
    "Name: {full_name}\n"
    "Tier: {tier_icon} {tier}\n"
    "Balance: ${balance:.2f}\n"
    "Total Spent: ${total_spent:.2f}\n"
    "Total Orders: {total_orders}\n"
    "Joined: {joined_at}\n"
)

ORDER_HISTORY_TITLE = "Recent Orders\n\n"
ORDER_ITEM_TEMPLATE = "Order #{order_id}\n   {product_name} - ${total:.2f}\n   Status: {status}\n\n"


def get_profile_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Topup Balance", callback_data="topup")],
        [InlineKeyboardButton(text="Order History", callback_data="order_history")],
        [InlineKeyboardButton(text="Transactions", callback_data="transactions")],
        [InlineKeyboardButton(text="Back", callback_data="back_main")]
    ])


def get_order_history_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Back to Profile", callback_data="profile_view")]
    ])


@router.callback_query(F.data == "profile_view")
async def view_profile(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = db.get_or_create_user(user_id, callback.from_user.username, callback.from_user.first_name)

    orders = db.get_user_orders(user_id)
    tier = user.get('tier', 'bronze')
    tier_icon = TIER_EMOJI.get(tier, "")

    joined_at = user.get('created_at', '')
    if joined_at:
        joined_at = joined_at[:10]

    text = PROFILE_TEMPLATE.format(
        user_id=user_id,
        full_name=callback.from_user.full_name,
        tier_icon=tier_icon,
        tier=tier.title(),
        balance=float(user.get('balance', 0.0)),
        total_spent=float(user.get('total_spent', 0.0)),
        total_orders=len(orders),
        joined_at=joined_at or 'Recently'
    )

    keyboard = get_profile_keyboard()

    try:
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    except Exception:
        await callback.message.delete()
        await callback.message.answer(text, reply_markup=keyboard, parse_mode="Markdown")

    await callback.answer()


@router.callback_query(F.data == "order_history")
async def view_order_history(callback: CallbackQuery):
    user_id = callback.from_user.id
    orders = db.get_user_orders(user_id, limit=10)

    if not orders:
        await callback.answer("No orders found", show_alert=True)
        return

    text = ORDER_HISTORY_TITLE

    for order in orders:
        items = order.get('order_items', [])
        product_names = []

        for item in items:
            product = item.get('products')
            if product:
                product_names.append(product['name'])

        product_str = ', '.join(product_names) if product_names else 'Unknown'

        text += ORDER_ITEM_TEMPLATE.format(
            order_id=order['id'],
            product_name=product_str[:30],
            total=float(order.get('total', 0)),
            status=order.get('status', 'unknown').title()
        )

    keyboard = get_order_history_keyboard()

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "transactions")
async def view_transactions(callback: CallbackQuery):
    user_id = callback.from_user.id
    transactions = db.get_transactions(user_id, limit=10)

    if not transactions:
        await callback.answer("No transactions found", show_alert=True)
        return

    text = "Transaction History\n\n"

    for tx in transactions:
        amount = float(tx['amount'])
        sign = "+" if amount > 0 else ""
        tx_type = tx.get('type', 'unknown').title()
        date = tx.get('created_at', '')[:10] if tx.get('created_at') else ''

        text += f"{sign}${amount:.2f} - {tx_type}\n"
        if tx.get('description'):
            text += f"   {tx['description'][:30]}\n"
        text += f"   {date}\n\n"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Back to Profile", callback_data="profile_view")]
    ])

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()
