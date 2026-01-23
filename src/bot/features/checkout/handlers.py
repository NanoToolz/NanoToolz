from aiogram import Router, F
from aiogram.types import CallbackQuery

from src.config import settings
from src.database import SessionLocal
from src.services.cart import get_cart_items, get_cart_totals, clear_cart
from src.services.orders import create_payment_from_cart, complete_payment, cancel_payment
from src.services.settings import get_setting
from .messages import (
    CHECKOUT_EMPTY,
    CHECKOUT_TITLE,
    PAYMENT_CHOOSE,
    PAYMENT_INSTRUCTIONS,
    PAYMENT_CONFIRMED,
    PAYMENT_NO_DELIVERY,
    PAYMENT_CANCELLED,
)
from .keyboards import payment_method_keyboard, payment_action_keyboard

router = Router()


def _wallet_for_method(db, method: str) -> tuple[str, str]:
    if method == "usdt_tron":
        wallet = get_setting(db, "payment_usdt_tron_wallet", settings.PAYMENT_WALLET_TRON)
        return wallet or settings.PAYMENT_WALLET_TRON, "USDT"
    wallet = get_setting(db, "payment_ltc_wallet", settings.PAYMENT_WALLET_LTC)
    return wallet or settings.PAYMENT_WALLET_LTC, "LTC"


@router.callback_query(F.data == "checkout")
async def checkout_start(query: CallbackQuery) -> None:
    db = SessionLocal()
    try:
        items = get_cart_items(db, query.from_user.id)
        total_usd, total_usdt = get_cart_totals(db, query.from_user.id)
    finally:
        db.close()

    if not items:
        await query.message.edit_text(CHECKOUT_EMPTY, parse_mode="HTML")
        await query.answer()
        return

    await query.message.edit_text(
        f"{CHECKOUT_TITLE.format(usd=total_usd, usdt=total_usdt)}\n\n{PAYMENT_CHOOSE}",
        parse_mode="HTML",
        reply_markup=payment_method_keyboard(),
    )
    await query.answer()


@router.callback_query(F.data.startswith("pay_"))
async def checkout_payment(query: CallbackQuery) -> None:
    parts = query.data.split("_")
    if len(parts) >= 3 and parts[1] == "usdt" and parts[2] == "tron":
        method = "usdt_tron"
    else:
        method = "ltc"

    db = SessionLocal()
    try:
        items = get_cart_items(db, query.from_user.id)
        if not items:
            await query.message.edit_text(CHECKOUT_EMPTY, parse_mode="HTML")
            await query.answer()
            return

        wallet, currency = _wallet_for_method(db, method)
        payment = create_payment_from_cart(
            db,
            user_id=query.from_user.id,
            items=items,
            method=method,
            currency=currency,
            wallet_to=wallet,
        )
        clear_cart(db, query.from_user.id)
        notice = get_setting(
            db,
            "payment_notice",
            "Send the exact amount and tap 'I Paid' after payment.",
        )
    finally:
        db.close()

    await query.message.edit_text(
        PAYMENT_INSTRUCTIONS.format(
            amount=float(payment.amount),
            currency=payment.currency,
            wallet=wallet,
            notice=notice,
            payment_ref=payment.payment_ref,
        ),
        parse_mode="HTML",
        reply_markup=payment_action_keyboard(payment.payment_ref),
    )
    await query.answer()


@router.callback_query(F.data.startswith("confirm_pay_"))
async def confirm_payment(query: CallbackQuery) -> None:
    payment_ref = query.data.split("_")[2]
    db = SessionLocal()
    try:
        deliveries = complete_payment(db, payment_ref)
    finally:
        db.close()

    if deliveries:
        lines = [PAYMENT_CONFIRMED]
        for delivery in deliveries:
            lines.append(f"\n<b>{delivery['product_name']}</b>\n{delivery['content']}")
        message = "".join(lines)
    else:
        message = PAYMENT_NO_DELIVERY

    await query.message.edit_text(message, parse_mode="HTML")
    await query.answer()


@router.callback_query(F.data.startswith("cancel_pay_"))
async def cancel_payment_handler(query: CallbackQuery) -> None:
    payment_ref = query.data.split("_")[2]
    db = SessionLocal()
    try:
        cancel_payment(db, payment_ref)
    finally:
        db.close()

    await query.message.edit_text(PAYMENT_CANCELLED, parse_mode="HTML")
    await query.answer()
