from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from src.database import SessionLocal
from src.services.cart import get_cart_items, get_cart_totals, update_quantity, remove_item, clear_cart
from src.services.pricing import calculate_current_price
from src.logger import logger
from src.middleware.rate_limiter import check_rate_limit
from .messages import CART_EMPTY, CART_TITLE, CART_TOTAL
from .keyboards import cart_keyboard

router = Router()


def _build_cart_message(items, total_usd: float, total_usdt: float) -> str:
    lines = [CART_TITLE, ""]
    for item in items:
        current_price = calculate_current_price(item.product, "USD")
        price = current_price * item.quantity
        lines.append(f"• {item.product.name} x{item.quantity} = ${price:.2f}")
    lines.append(CART_TOTAL.format(usd=total_usd, usdt=total_usdt))
    return "\n".join(lines)


@router.callback_query(F.data == "cart")
async def cart_view(query: CallbackQuery) -> None:
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
        if not items:
            message = CART_EMPTY
            keyboard = None
        else:
            message = _build_cart_message(items, total_usd, total_usdt)
            keyboard = cart_keyboard(items)
    except Exception as exc:
        logger.error("Error in cart_view: %s", exc)
        await query.answer("❌ Something went wrong. Try again.", show_alert=True)
        return
    finally:
        db.close()

    if not items:
        await query.message.edit_text(message, parse_mode="HTML")
        await query.answer()
        return

    await query.message.edit_text(
        message,
        parse_mode="HTML",
        reply_markup=keyboard,
    )
    await query.answer()


@router.message(Command("cart"))
async def cart_view_command(message: Message) -> None:
    allowed, warn = check_rate_limit(message.from_user.id, with_warning=True)
    if not allowed:
        await message.answer("⏱️ Too many requests. Wait 30 seconds.")
        return
    if warn:
        await message.answer("⚠️ You're sending too many requests. Slow down.")

    db = SessionLocal()
    try:
        items = get_cart_items(db, message.from_user.id)
        total_usd, total_usdt = get_cart_totals(db, message.from_user.id)
        if not items:
            response = CART_EMPTY
            keyboard = None
        else:
            response = _build_cart_message(items, total_usd, total_usdt)
            keyboard = cart_keyboard(items)
    except Exception as exc:
        logger.error("Error in cart_view_command: %s", exc)
        await message.answer("❌ Something went wrong. Try again.")
        return
    finally:
        db.close()

    if not items:
        await message.answer(response, parse_mode="HTML")
        return

    await message.answer(
        response,
        parse_mode="HTML",
        reply_markup=keyboard,
    )


@router.callback_query(F.data == "cart_clear")
async def cart_clear(query: CallbackQuery) -> None:
    allowed, warn = check_rate_limit(query.from_user.id, with_warning=True)
    if not allowed:
        await query.answer("⏱️ Too many requests. Wait 30 seconds.", show_alert=True)
        return
    if warn:
        await query.answer("⚠️ You're sending too many requests. Slow down.", show_alert=True)

    db = SessionLocal()
    try:
        clear_cart(db, query.from_user.id)
    except Exception as exc:
        logger.error("Error in cart_clear: %s", exc)
        await query.answer("❌ Something went wrong. Try again.", show_alert=True)
        return
    finally:
        db.close()
    await cart_view(query)


@router.callback_query(F.data.startswith("cart_inc_"))
async def cart_inc(query: CallbackQuery) -> None:
    item_id = int(query.data.split("_")[2])
    allowed, warn = check_rate_limit(query.from_user.id, with_warning=True)
    if not allowed:
        await query.answer("⏱️ Too many requests. Wait 30 seconds.", show_alert=True)
        return
    if warn:
        await query.answer("⚠️ You're sending too many requests. Slow down.", show_alert=True)

    db = SessionLocal()
    try:
        update_quantity(db, item_id, 1)
    except Exception as exc:
        logger.error("Error in cart_inc: %s", exc)
        await query.answer("❌ Something went wrong. Try again.", show_alert=True)
        return
    finally:
        db.close()
    await cart_view(query)


@router.callback_query(F.data.startswith("cart_dec_"))
async def cart_dec(query: CallbackQuery) -> None:
    item_id = int(query.data.split("_")[2])
    allowed, warn = check_rate_limit(query.from_user.id, with_warning=True)
    if not allowed:
        await query.answer("⏱️ Too many requests. Wait 30 seconds.", show_alert=True)
        return
    if warn:
        await query.answer("⚠️ You're sending too many requests. Slow down.", show_alert=True)

    db = SessionLocal()
    try:
        update_quantity(db, item_id, -1)
    except Exception as exc:
        logger.error("Error in cart_dec: %s", exc)
        await query.answer("❌ Something went wrong. Try again.", show_alert=True)
        return
    finally:
        db.close()
    await cart_view(query)


@router.callback_query(F.data.startswith("cart_del_"))
async def cart_del(query: CallbackQuery) -> None:
    item_id = int(query.data.split("_")[2])
    allowed, warn = check_rate_limit(query.from_user.id, with_warning=True)
    if not allowed:
        await query.answer("⏱️ Too many requests. Wait 30 seconds.", show_alert=True)
        return
    if warn:
        await query.answer("⚠️ You're sending too many requests. Slow down.", show_alert=True)

    db = SessionLocal()
    try:
        remove_item(db, item_id)
    except Exception as exc:
        logger.error("Error in cart_del: %s", exc)
        await query.answer("❌ Something went wrong. Try again.", show_alert=True)
        return
    finally:
        db.close()
    await cart_view(query)


@router.callback_query(F.data == "noop")
async def noop(query: CallbackQuery) -> None:
    allowed = check_rate_limit(query.from_user.id)
    if not allowed:
        await query.answer("⏱️ Too many requests. Wait 30 seconds.", show_alert=True)
        return
    try:
        await query.answer()
    except Exception as exc:
        logger.error("Error in noop: %s", exc)
        await query.answer("❌ Something went wrong. Try again.", show_alert=True)
