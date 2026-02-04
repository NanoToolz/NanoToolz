from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from src.database import db
from src.logger import logger

router = Router()

TIER_EMOJI = {"bronze": "", "silver": "", "gold": "", "platinum": ""}


def get_welcome_text(first_name: str, user_id: int, tier: str = "bronze") -> str:
    custom_text = db.get_setting("welcome_message")
    tier_icon = TIER_EMOJI.get(tier, "")

    if custom_text and custom_text != "Welcome to NanoToolz! Browse our catalog to find what you need.":
        return custom_text.replace("{first_name}", first_name).replace("{user_id}", str(user_id))

    return (
        f"Welcome to NanoToolz!\n\n"
        f"Hi {first_name}!\n"
        f"Your ID: `{user_id}`\n"
        f"Tier: {tier_icon} {tier.title()}\n\n"
        f"Instant Delivery\n"
        f"Secure Payments\n"
        f"24/7 Support\n\n"
        f"Select an option below to get started:"
    )


MAIN_MENU_TEXT = "Main Menu\n\nSelect an option below:"


def get_main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Browse Catalog", callback_data="catalog_main")],
            [InlineKeyboardButton(text="View Cart", callback_data="cart_view")],
            [
                InlineKeyboardButton(text="Topup Balance", callback_data="topup"),
                InlineKeyboardButton(text="Profile", callback_data="profile_view")
            ],
            [
                InlineKeyboardButton(text="Referrals", callback_data="referrals"),
                InlineKeyboardButton(text="Wishlist", callback_data="wishlist")
            ],
            [
                InlineKeyboardButton(text="Daily Spin", callback_data="daily_spin"),
                InlineKeyboardButton(text="Help", callback_data="help_main")
            ],
            [InlineKeyboardButton(text="Support", callback_data="support")],
            [InlineKeyboardButton(text="Admin Panel", callback_data="admin_panel")]
        ]
    )


@router.message(CommandStart())
async def start_command(message: Message):
    logger.info(f"Received /start from user {message.from_user.id}")
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name or "User"

    referral_code = None
    if message.text and len(message.text.split()) > 1:
        referral_code = message.text.split()[1]

    user = db.get_user(user_id)

    if not user:
        referred_by = None
        if referral_code:
            referrer = db.get_user_by_referral_code(referral_code)
            if referrer and referrer["id"] != user_id:
                referred_by = referrer["id"]
                logger.info(f"User {user_id} referred by {referred_by}")

        user = db.create_user(user_id, username, first_name, referred_by)
        logger.info(f"New user registered: {user_id}")
    else:
        db.update_user(user_id, {"username": username, "first_name": first_name})

    tier = user.get("tier", "bronze")
    welcome_text = get_welcome_text(first_name, user_id, tier)
    keyboard = get_main_keyboard()

    custom_image = db.get_setting("welcome_image")

    if custom_image:
        try:
            await message.answer_photo(
                custom_image,
                caption=welcome_text,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
        except Exception:
            await message.answer(welcome_text, reply_markup=keyboard, parse_mode="Markdown")
    else:
        await message.answer(welcome_text, reply_markup=keyboard, parse_mode="Markdown")


@router.callback_query(F.data == "back_main")
async def back_to_main(callback: CallbackQuery):
    keyboard = get_main_keyboard()

    try:
        await callback.message.edit_text(MAIN_MENU_TEXT, reply_markup=keyboard, parse_mode="Markdown")
    except Exception:
        await callback.message.delete()
        await callback.message.answer(MAIN_MENU_TEXT, reply_markup=keyboard, parse_mode="Markdown")

    await callback.answer()
