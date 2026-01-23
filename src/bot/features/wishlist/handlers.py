from aiogram import Router, F
from aiogram.types import CallbackQuery

from src.database import SessionLocal
from src.database.models import WishlistItem
from src.services.cart import add_to_cart
from src.logger import logger
from src.middleware.rate_limiter import check_rate_limit
from .messages import WISHLIST_EMPTY, WISHLIST_TITLE
from .keyboards import wishlist_keyboard

router = Router()


@router.callback_query(F.data == "wishlist")
async def wishlist_view(query: CallbackQuery) -> None:
    allowed, warn = check_rate_limit(query.from_user.id, with_warning=True)
    if not allowed:
        await query.answer("⏱️ Too many requests. Wait 30 seconds.", show_alert=True)
        return
    if warn:
        await query.answer("⚠️ You're sending too many requests. Slow down.", show_alert=True)

    db = SessionLocal()
    try:
        items = db.query(WishlistItem).filter(WishlistItem.user_id == query.from_user.id).all()
        if not items:
            message = WISHLIST_EMPTY
            keyboard = None
        else:
            lines = [WISHLIST_TITLE, ""]
            for item in items:
                lines.append(f"• {item.product.name}")
            message = "\n".join(lines)
            keyboard = wishlist_keyboard(items)
    except Exception as exc:
        logger.error("Error in wishlist_view: %s", exc)
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


@router.callback_query(F.data.startswith("wishlist_add_"))
async def wishlist_add(query: CallbackQuery) -> None:
    allowed, warn = check_rate_limit(query.from_user.id, with_warning=True)
    if not allowed:
        await query.answer("⏱️ Too many requests. Wait 30 seconds.", show_alert=True)
        return
    if warn:
        await query.answer("⚠️ You're sending too many requests. Slow down.", show_alert=True)

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
    except Exception as exc:
        logger.error("Error in wishlist_add: %s", exc)
        await query.answer("❌ Something went wrong. Try again.", show_alert=True)
        return
    finally:
        db.close()

    await query.answer("⭐ Added to wishlist", show_alert=False)


@router.callback_query(F.data.startswith("wishlist_del_"))
async def wishlist_del(query: CallbackQuery) -> None:
    allowed, warn = check_rate_limit(query.from_user.id, with_warning=True)
    if not allowed:
        await query.answer("⏱️ Too many requests. Wait 30 seconds.", show_alert=True)
        return
    if warn:
        await query.answer("⚠️ You're sending too many requests. Slow down.", show_alert=True)

    item_id = int(query.data.split("_")[2])
    db = SessionLocal()
    try:
        item = db.query(WishlistItem).filter(WishlistItem.id == item_id).first()
        if item:
            db.delete(item)
            db.commit()
    except Exception as exc:
        logger.error("Error in wishlist_del: %s", exc)
        await query.answer("❌ Something went wrong. Try again.", show_alert=True)
        return
    finally:
        db.close()
    await wishlist_view(query)


@router.callback_query(F.data.startswith("wishlist_cart_"))
async def wishlist_add_cart(query: CallbackQuery) -> None:
    allowed, warn = check_rate_limit(query.from_user.id, with_warning=True)
    if not allowed:
        await query.answer("⏱️ Too many requests. Wait 30 seconds.", show_alert=True)
        return
    if warn:
        await query.answer("⚠️ You're sending too many requests. Slow down.", show_alert=True)

    product_id = int(query.data.split("_")[2])
    db = SessionLocal()
    try:
        add_to_cart(db, query.from_user.id, product_id, 1)
    except Exception as exc:
        logger.error("Error in wishlist_add_cart: %s", exc)
        await query.answer("❌ Something went wrong. Try again.", show_alert=True)
        return
    finally:
        db.close()
    await query.answer("✅ Added to cart", show_alert=False)
