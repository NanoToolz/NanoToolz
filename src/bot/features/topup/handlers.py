import uuid

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from src.config import settings
from src.database import SessionLocal
from src.database.models import User, Payment
from src.services.settings import get_setting
from src.logger import logger
from src.middleware.rate_limiter import check_rate_limit
from src.utils.validators import validate_positive_number
from .keyboards import topup_amount_keyboard, topup_confirm_keyboard
from .messages import TOPUP_TITLE, TOPUP_INSTRUCTIONS

router = Router()


@router.callback_query(F.data == "topup")
async def topup_menu(query: CallbackQuery) -> None:
    allowed, warn = check_rate_limit(query.from_user.id, with_warning=True)
    if not allowed:
        await query.answer("⏱️ Too many requests. Wait 30 seconds.", show_alert=True)
        return
    if warn:
        await query.answer("⚠️ You're sending too many requests. Slow down.", show_alert=True)

    try:
        await query.message.edit_text(
            TOPUP_TITLE,
            parse_mode="HTML",
            reply_markup=topup_amount_keyboard(),
        )
        await query.answer()
    except Exception as exc:
        logger.error("Error in topup_menu: %s", exc)
        await query.answer("❌ Something went wrong. Try again.", show_alert=True)


@router.message(Command("topup"))
async def topup_command(message: Message) -> None:
    allowed, warn = check_rate_limit(message.from_user.id, with_warning=True)
    if not allowed:
        await message.answer("⏱️ Too many requests. Wait 30 seconds.")
        return
    if warn:
        await message.answer("⚠️ You're sending too many requests. Slow down.")
    try:
        await message.answer(
            TOPUP_TITLE,
            parse_mode="HTML",
            reply_markup=topup_amount_keyboard(),
        )
    except Exception as exc:
        logger.error("Error in topup_command: %s", exc)
        await message.answer("❌ Something went wrong. Try again.")


@router.callback_query(F.data.startswith("topup_"))
async def topup_select_amount(query: CallbackQuery) -> None:
    allowed, warn = check_rate_limit(query.from_user.id, with_warning=True)
    if not allowed:
        await query.answer("⏱️ Too many requests. Wait 30 seconds.", show_alert=True)
        return
    if warn:
        await query.answer("⚠️ You're sending too many requests. Slow down.", show_alert=True)

    amount_str = query.data.split("_")[1]
    if not validate_positive_number(amount_str):
        await query.answer("❌ Invalid amount.", show_alert=True)
        return

    amount_usd = float(amount_str)
    amount_usdt = amount_usd * 0.99

    db = SessionLocal()
    try:
        payment_ref = uuid.uuid4().hex
        wallet = get_setting(db, "payment_usdt_tron_wallet", settings.PAYMENT_WALLET_TRON)
        user = db.query(User).filter(User.telegram_id == query.from_user.id).first()
        if not user:
            await query.answer("❌ User not found.", show_alert=True)
            return

        payment = Payment(
            user_id=user.id,
            payment_ref=payment_ref,
            amount=amount_usdt,
            currency="USDT",
            method="topup_usdt",
            wallet_to=wallet,
            status="pending",
            confirmations=0,
        )
        db.add(payment)
        db.commit()
    except Exception as exc:
        logger.error("Error in topup_select_amount: %s", exc)
        await query.answer("❌ Something went wrong. Try again.", show_alert=True)
        return
    finally:
        db.close()

    message = TOPUP_INSTRUCTIONS.format(
        amount=amount_usdt,
        wallet=wallet,
        payment_ref=payment_ref,
    )

    await query.message.edit_text(
        message,
        parse_mode="HTML",
        reply_markup=topup_confirm_keyboard(payment_ref, amount_usd),
    )
    await query.answer()


@router.callback_query(F.data.startswith("confirm_topup_"))
async def confirm_topup(query: CallbackQuery) -> None:
    allowed, warn = check_rate_limit(query.from_user.id, with_warning=True)
    if not allowed:
        await query.answer("⏱️ Too many requests. Wait 30 seconds.", show_alert=True)
        return
    if warn:
        await query.answer("⚠️ You're sending too many requests. Slow down.", show_alert=True)

    parts = query.data.split("_")
    if len(parts) < 4:
        await query.answer("❌ Invalid request.", show_alert=True)
        return

    payment_ref = parts[2]
    amount_usd = float(parts[3])

    db = SessionLocal()
    try:
        payment = db.query(Payment).filter(Payment.payment_ref == payment_ref).first()
        user = db.query(User).filter(User.telegram_id == query.from_user.id).first()
        if not payment or not user:
            await query.answer("❌ Payment not found.", show_alert=True)
            return

        payment.status = "confirmed"
        user.credits = float(user.credits) + amount_usd
        db.commit()

        await query.message.edit_text(
            "✅ <b>Topup Successful!</b>\n\n"
            f"💰 Added: ${amount_usd:.2f}\n"
            f"💵 New Balance: ${float(user.credits):.2f}",
            parse_mode="HTML",
        )
    except Exception as exc:
        logger.error("Error in confirm_topup: %s", exc)
        await query.answer("❌ Something went wrong. Try again.", show_alert=True)
        return
    finally:
        db.close()

    await query.answer()
