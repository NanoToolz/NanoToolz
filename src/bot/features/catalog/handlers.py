from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from sqlalchemy import func

from src.database import SessionLocal
from src.database.models import Category, Product, Review
from src.services.cart import add_to_cart as add_item_to_cart
from src.services.pricing import get_price_display_info
from src.logger import logger
from src.middleware.rate_limiter import check_rate_limit
from .keyboards import (
    categories_keyboard,
    products_keyboard,
    product_detail_keyboard,
    review_rating_keyboard,
)
from .messages import (
    CATEGORIES_TITLE,
    PRODUCTS_TITLE,
    PRODUCT_NOT_FOUND,
    REVIEWS_TITLE,
    REVIEWS_EMPTY,
    REVIEW_PROMPT,
)

router = Router()


@router.message(Command("shop"))
async def shop_command(message: Message) -> None:
    """Direct shop command"""
    allowed, warn = check_rate_limit(message.from_user.id, with_warning=True)
    if not allowed:
        await message.answer("⏱️ Too many requests. Wait 30 seconds.")
        return
    if warn:
        await message.answer("⚠️ You're sending too many requests. Slow down.")
    try:
        await _send_categories_message(message)
    except Exception as exc:
        logger.error("Error in shop_command: %s", exc)
        await message.answer("❌ Something went wrong. Try again.")


@router.callback_query(F.data == "browse")
async def browse_callback(query: CallbackQuery) -> None:
    """Browse products by category"""
    allowed, warn = check_rate_limit(query.from_user.id, with_warning=True)
    if not allowed:
        await query.answer("⏱️ Too many requests. Wait 30 seconds.", show_alert=True)
        return
    if warn:
        await query.answer("⚠️ You're sending too many requests. Slow down.", show_alert=True)
    try:
        await _send_categories_callback(query)
    except Exception as exc:
        logger.error("Error in browse_callback: %s", exc)
        await query.answer("❌ Something went wrong. Try again.", show_alert=True)


async def _send_categories_message(message: Message) -> None:
    db = SessionLocal()
    try:
        categories = db.query(Category).filter(Category.featured == True).all()
    finally:
        db.close()

    await message.answer(
        CATEGORIES_TITLE,
        parse_mode="HTML",
        reply_markup=categories_keyboard(categories),
    )


async def _send_categories_callback(query: CallbackQuery) -> None:
    db = SessionLocal()
    try:
        categories = db.query(Category).filter(Category.featured == True).all()
    finally:
        db.close()

    await query.message.edit_text(
        CATEGORIES_TITLE,
        parse_mode="HTML",
        reply_markup=categories_keyboard(categories),
    )
    await query.answer()


@router.callback_query(F.data.startswith("category_"))
async def category_products(query: CallbackQuery) -> None:
    """Show products in category"""
    allowed, warn = check_rate_limit(query.from_user.id, with_warning=True)
    if not allowed:
        await query.answer("⏱️ Too many requests. Wait 30 seconds.", show_alert=True)
        return
    if warn:
        await query.answer("⚠️ You're sending too many requests. Slow down.", show_alert=True)

    category_id = int(query.data.split("_")[1])
    db = SessionLocal()
    try:
        products = (
            db.query(Product)
            .filter(Product.category_id == category_id, Product.status == "published")
            .all()
        )
    except Exception as exc:
        logger.error("Error in category_products: %s", exc)
        await query.answer("❌ Something went wrong. Try again.", show_alert=True)
        return
    finally:
        db.close()

    await query.message.edit_text(
        PRODUCTS_TITLE.format(count=len(products)),
        parse_mode="HTML",
        reply_markup=products_keyboard(products),
    )
    await query.answer()


@router.callback_query(F.data.startswith("product_"))
async def product_detail(query: CallbackQuery) -> None:
    """Show product detail"""
    allowed, warn = check_rate_limit(query.from_user.id, with_warning=True)
    if not allowed:
        await query.answer("⏱️ Too many requests. Wait 30 seconds.", show_alert=True)
        return
    if warn:
        await query.answer("⚠️ You're sending too many requests. Slow down.", show_alert=True)

    product_id = int(query.data.split("_")[1])
    db = SessionLocal()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            await query.answer(PRODUCT_NOT_FOUND, show_alert=True)
            return

        price_info = get_price_display_info(product)
        if price_info["status"] == "new":
            price_text = (
                f"💰 ${price_info['current_price_usd']:.2f} "
                f"(≈ {price_info['current_price_usdt']:.2f} USDT)"
            )
        elif price_info["status"] == "at_minimum":
            price_text = (
                f"💰 <s>${price_info['initial_price_usd']:.2f}</s> → "
                f"${price_info['current_price_usd']:.2f} (MINIMUM)\n"
                f"≈ {price_info['current_price_usdt']:.2f} USDT"
            )
        else:
            discount = price_info["discount_percentage"]
            price_text = (
                f"💰 <s>${price_info['initial_price_usd']:.2f}</s> → "
                f"${price_info['current_price_usd']:.2f} ({discount:.0f}% OFF)\n"
                f"≈ {price_info['current_price_usdt']:.2f} USDT\n"
                f"📉 Drops ${price_info['daily_drop_usd']:.2f}/day "
                f"({price_info['days_until_minimum']} days left)"
            )

        if product.stock is None:
            stock_status = "✅ In Stock (Unlimited)"
        elif product.stock > 0:
            stock_status = f"✅ In Stock ({product.stock})"
        else:
            stock_status = "❌ Out of Stock"

        await query.message.edit_text(
            f"<b>{product.name}</b>\n\n"
            f"{price_text}\n"
            f"⭐ {product.rating}/5 ({product.review_count} reviews)\n"
            f"🛍️ {product.sales_count} sold\n"
            f"📦 {stock_status}\n\n"
            f"{product.description}",
            parse_mode="HTML",
            reply_markup=product_detail_keyboard(product.id),
        )
    except Exception as exc:
        logger.error("Error in product_detail: %s", exc)
        await query.answer("❌ Something went wrong. Try again.", show_alert=True)
        return
    finally:
        db.close()

    await query.answer()


@router.callback_query(F.data.startswith("add_cart_"))
async def add_to_cart(query: CallbackQuery) -> None:
    """Add product to cart"""
    allowed, warn = check_rate_limit(query.from_user.id, with_warning=True)
    if not allowed:
        await query.answer("⏱️ Too many requests. Wait 30 seconds.", show_alert=True)
        return
    if warn:
        await query.answer("⚠️ You're sending too many requests. Slow down.", show_alert=True)

    product_id = int(query.data.split("_")[2])
    db = SessionLocal()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            await query.answer(PRODUCT_NOT_FOUND, show_alert=True)
            return
        if product.stock is not None and product.stock <= 0:
            await query.answer("❌ Out of stock", show_alert=True)
            return
        add_item_to_cart(db, query.from_user.id, product_id, 1)
    except Exception as exc:
        logger.error("Error in add_to_cart: %s", exc)
        await query.answer("❌ Something went wrong. Try again.", show_alert=True)
        return
    finally:
        db.close()

    await query.answer("✅ Added to cart!", show_alert=False)


@router.callback_query(F.data.startswith("reviews_"))
async def reviews_view(query: CallbackQuery) -> None:
    allowed, warn = check_rate_limit(query.from_user.id, with_warning=True)
    if not allowed:
        await query.answer("⏱️ Too many requests. Wait 30 seconds.", show_alert=True)
        return
    if warn:
        await query.answer("⚠️ You're sending too many requests. Slow down.", show_alert=True)

    product_id = int(query.data.split("_")[1])
    db = SessionLocal()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            await query.answer(PRODUCT_NOT_FOUND, show_alert=True)
            return
        reviews = (
            db.query(Review)
            .filter(Review.product_id == product_id)
            .order_by(Review.created_at.desc())
            .limit(5)
            .all()
        )
    except Exception as exc:
        logger.error("Error in reviews_view: %s", exc)
        await query.answer("❌ Something went wrong. Try again.", show_alert=True)
        return
    finally:
        db.close()

    lines = [REVIEWS_TITLE]
    if reviews:
        for review in reviews:
            comment = review.comment or "No comment"
            lines.append(f"⭐ {review.rating}/5 - {comment}")
    else:
        lines.append(REVIEWS_EMPTY)

    lines.append("")
    lines.append(REVIEW_PROMPT)

    await query.message.edit_text(
        "\n".join(lines),
        parse_mode="HTML",
        reply_markup=review_rating_keyboard(product_id),
    )
    await query.answer()


@router.callback_query(F.data.startswith("review_rate_"))
async def review_rate(query: CallbackQuery) -> None:
    allowed, warn = check_rate_limit(query.from_user.id, with_warning=True)
    if not allowed:
        await query.answer("⏱️ Too many requests. Wait 30 seconds.", show_alert=True)
        return
    if warn:
        await query.answer("⚠️ You're sending too many requests. Slow down.", show_alert=True)

    parts = query.data.split("_")
    product_id = int(parts[2])
    rating = int(parts[3])

    db = SessionLocal()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            await query.answer(PRODUCT_NOT_FOUND, show_alert=True)
            return

        existing = (
            db.query(Review)
            .filter(
                Review.product_id == product_id,
                Review.user_id == query.from_user.id,
            )
            .first()
        )
        if existing:
            existing.rating = rating
        else:
            db.add(
                Review(
                    user_id=query.from_user.id,
                    product_id=product_id,
                    rating=rating,
                )
            )
        db.commit()

        avg_rating, total_reviews = db.query(
            func.avg(Review.rating),
            func.count(Review.id),
        ).filter(Review.product_id == product_id).first()
        product.rating = float(avg_rating or 0)
        product.review_count = int(total_reviews or 0)
        db.commit()
    except Exception as exc:
        logger.error("Error in review_rate: %s", exc)
        await query.answer("❌ Something went wrong. Try again.", show_alert=True)
        return
    finally:
        db.close()

    await query.answer("✅ Thanks for your review!", show_alert=True)
