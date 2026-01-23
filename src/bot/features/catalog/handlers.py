from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from sqlalchemy import func

from src.database import SessionLocal
from src.database.models import Category, Product, Review
from src.services.cart import add_to_cart as add_item_to_cart
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
    await _send_categories_message(message)


@router.callback_query(F.data == "browse")
async def browse_callback(query: CallbackQuery) -> None:
    """Browse products by category"""
    await _send_categories_callback(query)


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
    category_id = int(query.data.split("_")[1])
    db = SessionLocal()
    try:
        products = (
            db.query(Product)
            .filter(Product.category_id == category_id, Product.status == "published")
            .all()
        )
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
    product_id = int(query.data.split("_")[1])
    db = SessionLocal()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            await query.answer(PRODUCT_NOT_FOUND, show_alert=True)
            return

        if product.stock is None:
            stock_status = "✅ In Stock (Unlimited)"
        elif product.stock > 0:
            stock_status = f"✅ In Stock ({product.stock})"
        else:
            stock_status = "❌ Out of Stock"

        await query.message.edit_text(
            f"<b>{product.name}</b>\n\n"
            f"💰 ${product.price_usd} (≈ {product.price_usdt} USDT)\n"
            f"⭐ {product.rating}/5 ({product.review_count} reviews)\n"
            f"🛍️ {product.sales_count} sold\n"
            f"📦 {stock_status}\n\n"
            f"{product.description}",
            parse_mode="HTML",
            reply_markup=product_detail_keyboard(product.id),
        )
    finally:
        db.close()

    await query.answer()


@router.callback_query(F.data.startswith("add_cart_"))
async def add_to_cart(query: CallbackQuery) -> None:
    """Add product to cart"""
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
    finally:
        db.close()

    await query.answer("✅ Added to cart!", show_alert=False)


@router.callback_query(F.data.startswith("reviews_"))
async def reviews_view(query: CallbackQuery) -> None:
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
    finally:
        db.close()

    await query.answer("✅ Thanks for your review!", show_alert=True)
