"""
Catalog feature - browse products by category
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm import Session

from src.database import get_db
from src.database.models import Category, Product, CartItem, User
from src.logger import logger

router = Router()

@router.callback_query(F.data == "catalog_main")
async def show_categories(callback: CallbackQuery):
    """Show category list"""
    db: Session = next(get_db())
    
    categories = db.query(Category).all()
    
    if not categories:
        await callback.answer("No categories available", show_alert=True)
        db.close()
        return
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=f"{cat.emoji} {cat.name}",
                callback_data=f"cat_{cat.id}"
            )]
            for cat in categories
        ] + [
            [InlineKeyboardButton(text="⬅️ Back", callback_data="back_main")]
        ]
    )
    
    text = "📚 Select a Category:\n\nBrowse our products by category"
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()
    db.close()

@router.callback_query(F.data.startswith("cat_"))
async def show_products(callback: CallbackQuery):
    """Show products in category"""
    db: Session = next(get_db())
    
    cat_id = int(callback.data.split("_")[1])
    category = db.query(Category).filter(Category.id == cat_id).first()
    
    if not category:
        await callback.answer("Category not found", show_alert=True)
        db.close()
        return
    
    products = db.query(Product).filter(Product.category_id == cat_id).all()
    
    if not products:
        text = f"No products in {category.name}"
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="⬅️ Back", callback_data="catalog_main")]
            ]
        )
        await callback.message.edit_text(text, reply_markup=keyboard)
        db.close()
        return
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=f"{prod.name} - ${prod.price_usd}",
                callback_data=f"prod_{prod.id}"
            )]
            for prod in products
        ] + [
            [InlineKeyboardButton(text="⬅️ Back", callback_data="catalog_main")]
        ]
    )
    
    text = f"📦 {category.name}\n\nSelect a product:"
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()
    db.close()

@router.callback_query(F.data.startswith("prod_"))
async def show_product(callback: CallbackQuery):
    """Show product details"""
    db: Session = next(get_db())
    
    prod_id = int(callback.data.split("_")[1])
    product = db.query(Product).filter(Product.id == prod_id).first()
    
    if not product:
        await callback.answer("Product not found", show_alert=True)
        db.close()
        return
    
    text = (
        f"📦 {product.name}\n\n"
        f"Price: ${product.price_usd}\n"
        f"Stock: {product.stock if product.stock else '∞'}\n\n"
        f"Description: {product.description}\n\n"
        f"Rating: ⭐ {product.rating}/5 ({product.review_count} reviews)"
    )
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Add to Cart", callback_data=f"addcart_{prod_id}")],
            [InlineKeyboardButton(text="⬅️ Back", callback_data=f"cat_{product.category_id}")]
        ]
    )
    
    if product.image_url:
        try:
            media = InputMediaPhoto(media=product.image_url, caption=text)
            await callback.message.edit_media(media, reply_markup=keyboard)
        except Exception:
            await callback.message.edit_text(text, reply_markup=keyboard)
    else:
        await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()
    db.close()

@router.callback_query(F.data.startswith("addcart_"))
async def add_to_cart(callback: CallbackQuery):
    """Add product to cart"""
    db: Session = next(get_db())
    
    prod_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id
    
    user = db.query(User).filter(User.telegram_id == user_id).first()
    if not user:
        await callback.answer("User not found", show_alert=True)
        db.close()
        return
    
    # Check if already in cart
    existing = db.query(CartItem).filter(
        CartItem.user_id == user.id,
        CartItem.product_id == prod_id
    ).first()
    
    if existing:
        existing.quantity += 1
    else:
        cart_item = CartItem(user_id=user.id, product_id=prod_id, quantity=1)
        db.add(cart_item)
    
    db.commit()
    await callback.answer("✅ Added to cart!", show_alert=False)
    logger.info(f"User {user_id} added product {prod_id} to cart")
    db.close()