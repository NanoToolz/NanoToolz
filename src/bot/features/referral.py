from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from src.database import db
from src.config import settings

router = Router()

REFERRAL_MENU = (
    "Referral Program\n\n"
    "Earn rewards by inviting friends!\n\n"
    f"Earn {settings.REFERRAL_COMMISSION}% commission on each referral purchase\n"
    "No limit on earnings\n"
    "Instant payouts to your balance"
)

REFERRAL_INFO = (
    "Your Referral Stats\n\n"
    "Referral Code: `{code}`\n"
    "Total Referrals: {count}\n"
    "Total Earned: ${earned:.2f}\n\n"
    "Share your link to earn commissions!"
)


def get_referral_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="My Referrals", callback_data="my_referrals")],
        [InlineKeyboardButton(text="Get Referral Link", callback_data="get_referral_link")],
        [InlineKeyboardButton(text="Back", callback_data="back_main")]
    ])


def get_referral_info_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Get Referral Link", callback_data="get_referral_link")],
        [InlineKeyboardButton(text="Back", callback_data="referrals")]
    ])


@router.callback_query(F.data == "referrals")
async def referral_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    db.get_or_create_user(user_id, callback.from_user.username, callback.from_user.first_name)

    keyboard = get_referral_menu_keyboard()

    try:
        await callback.message.edit_text(REFERRAL_MENU, reply_markup=keyboard, parse_mode="Markdown")
    except Exception:
        await callback.message.delete()
        await callback.message.answer(REFERRAL_MENU, reply_markup=keyboard, parse_mode="Markdown")

    await callback.answer()


@router.callback_query(F.data == "my_referrals")
async def my_referrals(callback: CallbackQuery):
    user_id = callback.from_user.id
    db.get_or_create_user(user_id, callback.from_user.username, callback.from_user.first_name)

    stats = db.get_referral_stats(user_id)

    text = REFERRAL_INFO.format(
        code=stats['referral_code'],
        count=stats['referral_count'],
        earned=stats['referral_earnings']
    )

    keyboard = get_referral_info_keyboard()

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "get_referral_link")
async def get_referral_link(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = db.get_or_create_user(user_id, callback.from_user.username, callback.from_user.first_name)

    referral_code = user.get('referral_code')

    bot_info = await callback.bot.get_me()
    referral_link = f"https://t.me/{bot_info.username}?start={referral_code}"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Back", callback_data="referrals")]
    ])

    await callback.message.answer(
        f"Your referral link:\n\n`{referral_link}`\n\nShare this link with friends. "
        f"You'll earn {settings.REFERRAL_COMMISSION}% commission on their purchases!",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer("Link generated!")
