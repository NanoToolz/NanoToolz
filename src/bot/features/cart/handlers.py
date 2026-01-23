from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from src.database import SessionLocal
from src.services.cart import get_cart_items, get_cart_totals, update_quantity, remove_item, clear_cart
from .messages import CART_EMPTY, CART_TITLE, CART_TOTAL
from .keyboards import cart_keyboard

router = Router()


def _build_cart_message(items, total_usd: float, total_usdt: float) -> str:
    lines = [CART_TITLE, ""]
    for item in items:
        price = float(item.product.price_usd) * item.quantity
        lines.append(f"• {item.product.name} x{item.quantity} = ${price:.2f}")
    lines.append(CART_TOTAL.format(usd=total_usd, usdt=total_usdt))
    return "\n".join(lines)


@router.callback_query(F.data == "cart")
async def cart_view(query: CallbackQuery) -> None:
    db = SessionLocal()
    try:
        items = get_cart_items(db, query.from_user.id)
        total_usd, total_usdt = get_cart_totals(db, query.from_user.id)
    finally:
        db.close()

    if not items:
        await query.message.edit_text(CART_EMPTY, parse_mode="HTML")
        await query.answer()
        return

    await query.message.edit_text(
        _build_cart_message(items, total_usd, total_usdt),
        parse_mode="HTML",
        reply_markup=cart_keyboard(items),
    )
    await query.answer()


@router.message(Command("cart"))
async def cart_view_command(message: Message) -> None:
    db = SessionLocal()
    try:
        items = get_cart_items(db, message.from_user.id)
        total_usd, total_usdt = get_cart_totals(db, message.from_user.id)
    finally:
        db.close()

    if not items:
        await message.answer(CART_EMPTY, parse_mode="HTML")
        return

    await message.answer(
        _build_cart_message(items, total_usd, total_usdt),
        parse_mode="HTML",
        reply_markup=cart_keyboard(items),
    )


@router.callback_query(F.data == "cart_clear")
async def cart_clear(query: CallbackQuery) -> None:
    db = SessionLocal()
    try:
        clear_cart(db, query.from_user.id)
    finally:
        db.close()
    await cart_view(query)


@router.callback_query(F.data.startswith("cart_inc_"))
async def cart_inc(query: CallbackQuery) -> None:
    item_id = int(query.data.split("_")[2])
    db = SessionLocal()
    try:
        update_quantity(db, item_id, 1)
    finally:
        db.close()
    await cart_view(query)


@router.callback_query(F.data.startswith("cart_dec_"))
async def cart_dec(query: CallbackQuery) -> None:
    item_id = int(query.data.split("_")[2])
    db = SessionLocal()
    try:
        update_quantity(db, item_id, -1)
    finally:
        db.close()
    await cart_view(query)


@router.callback_query(F.data.startswith("cart_del_"))
async def cart_del(query: CallbackQuery) -> None:
    item_id = int(query.data.split("_")[2])
    db = SessionLocal()
    try:
        remove_item(db, item_id)
    finally:
        db.close()
    await cart_view(query)


@router.callback_query(F.data == "noop")
async def noop(query: CallbackQuery) -> None:
    await query.answer()
