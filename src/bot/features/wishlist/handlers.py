from aiogram import Router, F
from aiogram.types import CallbackQuery

from src.database import SessionLocal
from src.database.models import WishlistItem
from src.services.cart import add_to_cart
from .messages import WISHLIST_EMPTY, WISHLIST_TITLE
from .keyboards import wishlist_keyboard

router = Router()


@router.callback_query(F.data == "wishlist")
async def wishlist_view(query: CallbackQuery) -> None:
    db = SessionLocal()
    try:
        items = db.query(WishlistItem).filter(WishlistItem.user_id == query.from_user.id).all()
    finally:
        db.close()

    if not items:
        await query.message.edit_text(WISHLIST_EMPTY, parse_mode="HTML")
        await query.answer()
        return

    lines = [WISHLIST_TITLE, ""]
    for item in items:
        lines.append(f"• {item.product.name}")

    await query.message.edit_text(
        "\n".join(lines),
        parse_mode="HTML",
        reply_markup=wishlist_keyboard(items),
    )
    await query.answer()


@router.callback_query(F.data.startswith("wishlist_add_"))
async def wishlist_add(query: CallbackQuery) -> None:
    product_id = int(query.data.split("_")[2])
    db = SessionLocal()
    try:
        existing = (
            db.query(WishlistItem)
            .filter(
                WishlistItem.user_id == query.from_user.id,
                WishlistItem.product_id == product_id,
            )
            .first()
        )
        if not existing:
            db.add(WishlistItem(user_id=query.from_user.id, product_id=product_id))
            db.commit()
    finally:
        db.close()

    await query.answer("⭐ Added to wishlist", show_alert=False)


@router.callback_query(F.data.startswith("wishlist_del_"))
async def wishlist_del(query: CallbackQuery) -> None:
    item_id = int(query.data.split("_")[2])
    db = SessionLocal()
    try:
        item = db.query(WishlistItem).filter(WishlistItem.id == item_id).first()
        if item:
            db.delete(item)
            db.commit()
    finally:
        db.close()
    await wishlist_view(query)


@router.callback_query(F.data.startswith("wishlist_cart_"))
async def wishlist_add_cart(query: CallbackQuery) -> None:
    product_id = int(query.data.split("_")[2])
    db = SessionLocal()
    try:
        add_to_cart(db, query.from_user.id, product_id, 1)
    finally:
        db.close()
    await query.answer("✅ Added to cart", show_alert=False)
