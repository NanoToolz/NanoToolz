"""
Admin feature - product and store management
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.orm import Session

from src.config import settings
from src.database import get_db
from src.database.models import Category, Product
from src.logger import logger

router = Router()

def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return user_id in settings.ADMIN_IDS

@router.callback_query(F.data == "admin_panel")
async def admin_panel(callback: CallbackQuery):
    """Admin panel main menu"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Admin access denied", show_alert=True)
        return
    
    text = (
        "🔐 Admin Panel\n\n"
        "Store Management Tools:"
    )
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📦 Manage Products", callback_data="admin_products")],
            [InlineKeyboardButton(text="📂 Manage Categories", callback_data="admin_categories")],
            [InlineKeyboardButton(text="📊 View Statistics", callback_data="admin_stats")],
            [InlineKeyboardButton(text="⬅️ Exit Admin", callback_data="back_main")]
        ]
    )
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data == "admin_products")
async def admin_products(callback: CallbackQuery):
    """Manage products"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Admin access denied", show_alert=True)
        return
    
    db: Session = next(get_db())
    products = db.query(Product).all()
    
    text = f"📦 Products ({len(products)} total)\n\n"
    
    if not products:
        text += "No products found"
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="➕ Add Product", callback_data="admin_add_product")],
                [InlineKeyboardButton(text="⬅️ Back", callback_data="admin_panel")]
            ]
        )
    else:
        for product in products[:10]:  # Show first 10
            status = "✅" if product.status == "published" else "⏳"
            text += f"{status} {product.name} - ${product.price_usd}\n"
        
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="➕ Add Product", callback_data="admin_add_product")],
                [InlineKeyboardButton(text="⬅️ Back", callback_data="admin_panel")]
            ]
        )
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()
    db.close()

@router.callback_query(F.data == "admin_categories")
async def admin_categories(callback: CallbackQuery):
    """Manage categories"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Admin access denied", show_alert=True)
        return
    
    db: Session = next(get_db())
    categories = db.query(Category).all()
    
    text = f"📂 Categories ({len(categories)} total)\n\n"
    
    if not categories:
        text += "No categories found"
    else:
        for cat in categories:
            text += f"{cat.emoji} {cat.name}\n"
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Add Category", callback_data="admin_add_category")],
            [InlineKeyboardButton(text="⬅️ Back", callback_data="admin_panel")]
        ]
    )
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()
    db.close()

@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    """View store statistics"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Admin access denied", show_alert=True)
        return
    
    db: Session = next(get_db())
    
    from src.database.models import User, Order
    
    total_users = db.query(User).count()
    total_orders = db.query(Order).count()
    total_revenue = sum([float(o.price_paid_usd) for o in db.query(Order).all()])
    total_products = db.query(Product).count()
    
    text = (
        f"📊 Store Statistics\n\n"
        f"👥 Total Users: {total_users}\n"
        f"📦 Total Products: {total_products}\n"
        f"📋 Total Orders: {total_orders}\n"
        f"💰 Total Revenue: ${total_revenue:.2f}\n\n"
        f"Status: ✅ All Systems Operational"
    )
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Back", callback_data="admin_panel")]
        ]
    )
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()
    db.close()

@router.callback_query(F.data == "admin_add_product")
async def admin_add_product(callback: CallbackQuery):
    """Placeholder for add product (requires web admin)"""
    text = (
        "➕ Add Product\n\n"
        "To add products, use the web admin panel:\n\n"
        "📍 URL: http://localhost:8000/admin\n"
        "👤 Login with your admin credentials\n\n"
        "Then navigate to: Products → Add New"
    )
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Back", callback_data="admin_products")]
        ]
    )
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data == "admin_add_category")
async def admin_add_category(callback: CallbackQuery):
    """Placeholder for add category"""
    text = (
        "➕ Add Category\n\n"
        "To add categories, use the web admin panel:\n\n"
        "📍 URL: http://localhost:8000/admin\n"
        "👤 Login with your admin credentials\n\n"
        "Then navigate to: Categories → Add New"
    )
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Back", callback_data="admin_categories")]
        ]
    )
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()