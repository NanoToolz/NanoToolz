import uuid

from aiogram import Router, F
from aiogram.types import CallbackQuery

from src.config import settings
from src.database import SessionLocal
from src.database.models import Order, Payment, User
from src.services.cart import get_cart_items, get_cart_totals, clear_cart
from src.services.orders import create_payment_from_cart, complete_payment, cancel_payment
from src.services.settings import get_setting
from src.services.pricing import calculate_current_price
from src.logger import logger
from src.middleware.rate_limiter import check_rate_limit
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
    allowed, warn = check_rate_limit(query.from_user.id, with_warning=True)
    if not allowed:
        await query.answer("⏱️ Too many requests. Wait 30 seconds.", show_alert=True)
        return
    if warn:
        await query.answer("⚠️ You're sending too many requests. Slow down.", show_alert=True)

    db = SessionLocal()
    try:
        items = get_cart_items(db, query.from_user.id)
        total_usd, total_usdt = get_cart_totals(db, query.from_user.id)
    except Exception as exc:
        logger.error("Error in checkout_start: %s", exc)
        await query.answer("❌ Something went wrong. Try again.", show_alert=True)
        return
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
    allowed, warn = check_rate_limit(query.from_user.id, with_warning=True)
    if not allowed:
        await query.answer("⏱️ Too many requests. Wait 30 seconds.", show_alert=True)
        return
    if warn:
        await query.answer("⚠️ You're sending too many requests. Slow down.", show_alert=True)

    parts = query.data.split("_")
    if len(parts) >= 3 and parts[1] == "usdt" and parts[2] == "tron":
        method = "usdt_tron"
    elif len(parts) >= 2 and parts[1] == "credits":
        method = "credits"
    else:
        method = "ltc"

    db = SessionLocal()
    try:
        items = get_cart_items(db, query.from_user.id)
        if not items:
            await query.message.edit_text(CHECKOUT_EMPTY, parse_mode="HTML")
            await query.answer()
            return

        total_usd, total_usdt = get_cart_totals(db, query.from_user.id)
        if method == "credits":
            user = db.query(User).filter(User.telegram_id == query.from_user.id).first()
            if not user:
                await query.answer("❌ User not found.", show_alert=True)
                return
            if float(user.credits) < total_usd:
                await query.answer("❌ Insufficient credits.", show_alert=True)
                return

            payment_ref = uuid.uuid4().hex
            for item in items:
                product_price_usd = calculate_current_price(item.product, "USD")
                product_price_usdt = calculate_current_price(item.product, "USDT")
                price_usd = product_price_usd * item.quantity
                price_usdt = product_price_usdt * item.quantity
                order = Order(
                    user_id=user.id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    price_paid_usd=price_usd,
                    price_paid_usdt=price_usdt,
                    payment_method="credits",
                    payment_ref=payment_ref,
                    payment_status="completed",
                    delivery_status="pending",
                )
                db.add(order)

            user.credits = float(user.credits) - total_usd
            db.add(
                Payment(
                    user_id=user.id,
                    payment_ref=payment_ref,
                    amount=total_usd,
                    currency="USD",
                    method="credits",
                    status="confirmed",
                    confirmations=0,
                )
            )
            db.commit()
            clear_cart(db, query.from_user.id)
            deliveries = complete_payment(db, payment_ref)

            if deliveries:
                lines = [PAYMENT_CONFIRMED]
                for delivery in deliveries:
                    lines.append(f"\n<b>{delivery['product_name']}</b>\n{delivery['content']}")
                message = "".join(lines)
            else:
                message = PAYMENT_NO_DELIVERY

            await query.message.edit_text(message, parse_mode="HTML")
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
    except Exception as exc:
        logger.error("Error in checkout_payment: %s", exc)
        await query.answer("❌ Something went wrong. Try again.", show_alert=True)
        return
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
    allowed, warn = check_rate_limit(query.from_user.id, with_warning=True)
    if not allowed:
        await query.answer("⏱️ Too many requests. Wait 30 seconds.", show_alert=True)
        return
    if warn:
        await query.answer("⚠️ You're sending too many requests. Slow down.", show_alert=True)

    payment_ref = query.data.split("_")[2]
    db = SessionLocal()
    try:
        deliveries = complete_payment(db, payment_ref)
    except Exception as exc:
        logger.error("Error in confirm_payment: %s", exc)
        await query.answer("❌ Something went wrong. Try again.", show_alert=True)
        return
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
    allowed, warn = check_rate_limit(query.from_user.id, with_warning=True)
    if not allowed:
        await query.answer("⏱️ Too many requests. Wait 30 seconds.", show_alert=True)
        return
    if warn:
        await query.answer("⚠️ You're sending too many requests. Slow down.", show_alert=True)

    payment_ref = query.data.split("_")[2]
    db = SessionLocal()
    try:
        cancel_payment(db, payment_ref)
    except Exception as exc:
        logger.error("Error in cancel_payment_handler: %s", exc)
        await query.answer("❌ Something went wrong. Try again.", show_alert=True)
        return
    finally:
        db.close()

    await query.message.edit_text(PAYMENT_CANCELLED, parse_mode="HTML")
    await query.answer()
