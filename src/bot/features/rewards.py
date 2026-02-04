import random
from datetime import datetime, date
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from src.database import db

router = Router()

TIER_INFO = {
    "bronze": {"discount": 0, "description": "Start your journey"},
    "silver": {"discount": 5, "description": "5% discount on all purchases"},
    "gold": {"discount": 10, "description": "10% discount on all purchases"},
    "platinum": {"discount": 15, "description": "15% discount + priority support"}
}

DAILY_SPIN_INTRO = (
    "Daily Spin\n\n"
    "Spin the wheel daily to win rewards!\n\n"
    "Win credits\n"
    "Win discount coupons\n"
    "Limited to 1 spin per day"
)

SPIN_RESULT_CREDITS = (
    "Congratulations!\n\n"
    "You won ${reward} in credits!\n\n"
    "Your balance has been updated."
)

SPIN_RESULT_NOTHING = (
    "Better luck tomorrow!\n\n"
    "You didn't win this time, but try again tomorrow!"
)

SPIN_ALREADY = "You already spun today! Come back tomorrow."


def get_daily_spin_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Spin Now", callback_data="spin_now")],
        [InlineKeyboardButton(text="Back", callback_data="back_main")]
    ])


def get_spin_result_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Shop Now", callback_data="catalog_main")],
        [InlineKeyboardButton(text="Back", callback_data="back_main")]
    ])


@router.callback_query(F.data == "daily_spin")
async def daily_spin_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = db.get_or_create_user(user_id, callback.from_user.username, callback.from_user.first_name)

    tier = user.get('tier', 'bronze')
    tier_info = TIER_INFO.get(tier, TIER_INFO['bronze'])

    text = (
        f"{DAILY_SPIN_INTRO}\n\n"
        f"Your Tier: {tier.title()}\n"
        f"Tier Benefit: {tier_info['description']}"
    )

    keyboard = get_daily_spin_keyboard()

    try:
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    except Exception:
        await callback.message.delete()
        await callback.message.answer(text, reply_markup=keyboard, parse_mode="Markdown")

    await callback.answer()


@router.callback_query(F.data == "spin_now")
async def spin_now(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = db.get_or_create_user(user_id, callback.from_user.username, callback.from_user.first_name)

    transactions = db.get_transactions(user_id, limit=50)
    today = date.today().isoformat()

    for tx in transactions:
        if tx.get('type') == 'spin' and tx.get('created_at', '')[:10] == today:
            await callback.answer(SPIN_ALREADY, show_alert=True)
            return

    tier = user.get('tier', 'bronze')

    rewards = [
        (0, 30),
        (1, 25),
        (2, 20),
        (5, 15),
        (10, 8),
        (25, 2),
    ]

    if tier == 'silver':
        rewards = [(r[0], r[1]) for r in rewards]
        rewards[3] = (5, 18)
        rewards[4] = (10, 10)
    elif tier == 'gold':
        rewards[3] = (5, 20)
        rewards[4] = (10, 12)
        rewards[5] = (25, 5)
    elif tier == 'platinum':
        rewards[2] = (2, 15)
        rewards[3] = (5, 25)
        rewards[4] = (10, 15)
        rewards[5] = (25, 8)

    total_weight = sum(w for _, w in rewards)
    rand = random.randint(1, total_weight)

    cumulative = 0
    reward_amount = 0
    for amount, weight in rewards:
        cumulative += weight
        if rand <= cumulative:
            reward_amount = amount
            break

    if reward_amount > 0:
        db.add_balance(user_id, reward_amount, f"Daily spin reward", "spin")
        text = SPIN_RESULT_CREDITS.format(reward=reward_amount)
    else:
        db.client.table("transactions").insert({
            "user_id": user_id,
            "type": "spin",
            "amount": 0,
            "description": "Daily spin - no win"
        }).execute()
        text = SPIN_RESULT_NOTHING

    keyboard = get_spin_result_keyboard()

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer("Spin complete!")
