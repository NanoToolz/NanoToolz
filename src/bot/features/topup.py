from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from src.database import db

router = Router()

TOPUP_INTRO = (
    "Add Funds\n\n"
    "Select the amount you want to topup:\n"
    "Minimum: $10\n"
    "Maximum: $1000"
)

TOPUP_PAYMENT_METHOD = (
    "Topup Amount: ${amount}\n\n"
    "Select Payment Gateway:"
)

TOPUP_SUCCESS = (
    "Payment Successful!\n\n"
    "Added: ${amount}\n"
    "New Balance: ${balance:.2f}"
)


def get_topup_amounts_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="$10", callback_data="topup_10"),
            InlineKeyboardButton(text="$20", callback_data="topup_20"),
            InlineKeyboardButton(text="$50", callback_data="topup_50")
        ],
        [
            InlineKeyboardButton(text="$100", callback_data="topup_100"),
            InlineKeyboardButton(text="$500", callback_data="topup_500")
        ],
        [InlineKeyboardButton(text="Back", callback_data="back_main")]
    ])


def get_payment_method_keyboard(amount: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Crypto (Mock)", callback_data=f"topup_crypto_{amount}")],
        [InlineKeyboardButton(text="Card (Mock)", callback_data=f"topup_card_{amount}")],
        [InlineKeyboardButton(text="Back", callback_data="topup")]
    ])


def get_topup_success_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="View Profile", callback_data="profile_view")],
        [InlineKeyboardButton(text="Shop Now", callback_data="catalog_main")]
    ])


@router.callback_query(F.data == "topup")
async def start_topup(callback: CallbackQuery):
    keyboard = get_topup_amounts_keyboard()

    try:
        await callback.message.edit_text(TOPUP_INTRO, reply_markup=keyboard, parse_mode="Markdown")
    except Exception:
        await callback.message.delete()
        await callback.message.answer(TOPUP_INTRO, reply_markup=keyboard, parse_mode="Markdown")

    await callback.answer()


@router.callback_query(F.data.startswith("topup_") & ~F.data.startswith("topup_crypto_") & ~F.data.startswith("topup_card_"))
async def select_payment_method(callback: CallbackQuery):
    try:
        amount = int(callback.data.split("_")[1])
    except (ValueError, IndexError):
        await callback.answer("Invalid amount", show_alert=True)
        return

    text = TOPUP_PAYMENT_METHOD.format(amount=amount)
    keyboard = get_payment_method_keyboard(amount)

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data.startswith("topup_crypto_") | F.data.startswith("topup_card_"))
async def process_mock_topup(callback: CallbackQuery):
    parts = callback.data.split("_")

    try:
        amount = int(parts[2])
    except (ValueError, IndexError):
        await callback.answer("Invalid request", show_alert=True)
        return

    if amount <= 0 or amount > 10000:
        await callback.answer("Invalid amount", show_alert=True)
        return

    user_id = callback.from_user.id
    db.get_or_create_user(user_id, callback.from_user.username, callback.from_user.first_name)

    new_balance = db.add_balance(user_id, amount, f"Topup ${amount}", "topup")

    text = TOPUP_SUCCESS.format(amount=amount, balance=new_balance)
    keyboard = get_topup_success_keyboard()

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer("Payment successful!")
