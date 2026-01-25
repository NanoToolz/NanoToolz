# ============================================
# FEATURE: Product Catalog
# ============================================
# Purpose: Browse products by category
# Users can view categories, products, and product details

# ===== IMPORTS =====
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from src.database.json_db import db

# Create router instance
router = Router()

# ============================================
# ===== MESSAGES SECTION =====
# ============================================
# All text messages for catalog feature

# Message shown when displaying categories
CATALOG_TITLE = "📚 **Catalog Categories**\nSelect a category to browse:"

# Error message when no categories available
NO_CATEGORIES = "🚫 No categories available"

# Error message when no products in category
NO_PRODUCTS = "🚫 No products found in **{category}**"

# Template for product detail display
# {name} = product name, {description} = product description
# {price} = product price, {status} = stock status
PRODUCT_DETAIL_TEMPLATE = (
    "📦 **{name}**\n\n"
    "📝 {description}\n\n"
    "💲 Price: **${price}**\n"
    "📊 Status: {status}\n"
)

# ============================================
# ===== KEYBOARDS SECTION =====
# ============================================
# All button layouts for catalog feature

def get_categories_keyboard(categories: list) -> InlineKeyboardMarkup:
    """
    Build keyboard with all product categories
    
    Args:
        categories: List of category objects from database
    
    Returns:
        Keyboard with category buttons
    """
    # Create button for each category
    buttons = [
        [InlineKeyboardButton(
            text=f"{cat['emoji']} {cat['name']}",  # Show emoji + category name
            callback_data=f"cat_{cat['id']}"  # Callback with category ID
        )]
        for cat in categories
    ]
    
    # Add back button at the end
    buttons.append([InlineKeyboardButton(text="⬅️ Back", callback_data="back_main")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_products_keyboard(products: list, cat_id: int) -> InlineKeyboardMarkup:
    """
    Build keyboard with products in a category
    
    Args:
        products: List of product objects
        cat_id: Category ID (for back button)
    
    Returns:
        Keyboard with product buttons
    """
    # Create button for each product showing name and price
    buttons = [
        [InlineKeyboardButton(
            text=f"📦 {p['name']} - ${p['price']}",
            callback_data=f"prod_{p['id']}"  # Callback with product ID
        )]
        for p in products
    ]
    
    # Add back button
    buttons.append([InlineKeyboardButton(text="⬅️ Back", callback_data="catalog_main")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_product_detail_keyboard(prod_id: int, cat_id: int) -> InlineKeyboardMarkup:
    """
    Build keyboard for product detail view
    
    Args:
        prod_id: Product ID
        cat_id: Category ID (for back button)
    
    Returns:
        Keyboard with "Add to Cart" and "Back" buttons
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Add to Cart", callback_data=f"add_cart_{prod_id}")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data=f"cat_{cat_id}")]
    ])

# ============================================
# ===== HANDLERS SECTION =====
# ============================================
# All handlers for catalog feature

@router.callback_query(F.data == "catalog_main")
async def show_categories(callback: CallbackQuery):
    """
    Show all product categories
    
    This handler runs when user clicks "Browse Catalog" button
    It fetches all categories from database and displays them
    """
    # Get all categories from database
    categories = db.get_categories()
    
    # Check if categories exist
    if not categories:
        # Show error if no categories
        await callback.answer(NO_CATEGORIES, show_alert=True)
        return
    
    # Build keyboard with categories
    keyboard = get_categories_keyboard(categories)
    
    # Edit message to show categories
    await callback.message.edit_text(
        CATALOG_TITLE,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    
    # Answer callback (removes loading state)
    await callback.answer()

@router.callback_query(F.data.startswith("cat_"))
async def show_products(callback: CallbackQuery):
    """
    Show products in selected category
    
    This handler runs when user clicks a category button
    It extracts category ID from callback_data and shows products
    """
    try:
        # Extract category ID from callback_data
        # callback_data format: "cat_5" -> extract "5"
        cat_id = int(callback.data.split("_")[1])
    except (ValueError, IndexError):
        # Show error if category ID is invalid
        await callback.answer("Invalid category", show_alert=True)
        return
    
    # Get category details from database
    category = db.get_category(cat_id)
    
    # Get all products in this category
    products = db.get_products(category_id=cat_id)
    
    # Check if products exist
    if not products:
        # Show error message with category name
        text = f"🚫 No products found in **{category['name']}**"
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="⬅️ Back", callback_data="catalog_main")]]
        )
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
        await callback.answer()
        return
    
    # Build keyboard with products
    keyboard = get_products_keyboard(products, cat_id)
    
    # Edit message to show products
    await callback.message.edit_text(
        f"📂 **{category['name']}**\nSelect a product:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    
    await callback.answer()

@router.callback_query(F.data.startswith("prod_"))
async def show_product_detail(callback: CallbackQuery):
    """
    Show product details
    
    This handler runs when user clicks a product button
    It shows product details with image, description, and price
    """
    try:
        # Extract product ID from callback_data
        # callback_data format: "prod_42" -> extract "42"
        prod_id = int(callback.data.split("_")[1])
    except (ValueError, IndexError):
        # Show error if product ID is invalid
        await callback.answer("Invalid product", show_alert=True)
        return
    
    # Get product details from database
    product = db.get_product(prod_id)
    
    # Check if product exists
    if not product:
        await callback.answer("Product not found", show_alert=True)
        return
    
    # Get stock count for this product
    stock = db.get_stock_count(prod_id)
    
    # Determine stock status message
    stock_status = f"✅ In Stock ({stock})" if stock > 0 else "❌ Out of Stock"
    
    # Build product detail text using template
    text = PRODUCT_DETAIL_TEMPLATE.format(
        name=product['name'],
        description=product.get('description', 'No description'),
        price=product['price'],
        status=stock_status
    )
    
    # Build keyboard with "Add to Cart" button
    keyboard = get_product_detail_keyboard(prod_id, product['category_id'])
    
    # Try to send with product image
    image_url = product.get("image_url")
    if not image_url:
        # Use placeholder image if no image URL
        image_url = "https://via.placeholder.com/300x200.png?text=NanoToolz"
    
    try:
        # Delete old message and send new one with image
        await callback.message.delete()
        await callback.message.answer_photo(
            photo=image_url,
            caption=text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
    except Exception:
        # Fallback to text-only message if image fails
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    
    await callback.answer()
