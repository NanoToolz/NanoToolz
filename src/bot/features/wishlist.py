# ============================================
# FEATURE: Wishlist
# ============================================
# Purpose: Save favorite products for later
# Users can add/remove products from wishlist

from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

# ============================================
# ===== MESSAGES SECTION =====
# ============================================

WISHLIST_EMPTY = (
    "⭐ **Your Wishlist is Empty**\n\n"
    "Add products to your wishlist to save them for later!"
)

WISHLIST_TITLE = "⭐ **Your Wishlist**\n\n"

# ============================================
# ===== KEYBOARDS SECTION =====
# ============================================

def get_empty_wishlist_keyboard() -> InlineKeyboardMarkup:
    """Build empty wishlist keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍️ Browse Catalog", callback_data="catalog_main")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="back_main")]
    ])

def get_wishlist_keyboard() -> InlineKeyboardMarkup:
    """Build wishlist keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍️ Browse Catalog", callback_data="catalog_main")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="back_main")]
    ])

# ============================================
# ===== HANDLERS SECTION =====
# ============================================

@router.callback_query(F.data == "wishlist")
async def wishlist_view(callback: CallbackQuery):
    """
    Display user's wishlist
    
    Shows saved products or empty message
    """
    user_id = callback.from_user.id
    
    # Placeholder - in real app, fetch from database
    # For now, show empty wishlist
    
    text = WISHLIST_EMPTY
    keyboard = get_empty_wishlist_keyboard()
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data.startswith("wishlist_add_"))
async def wishlist_add(callback: CallbackQuery):
    """
    Add product to wishlist
    
    Extracts product ID and saves to wishlist
    """
    try:
        # Extract product ID from callback_data
        # Format: "wishlist_add_42" -> extract "42"
        product_id = int(callback.data.split("_")[2])
    except (ValueError, IndexError):
        await callback.answer("Invalid product", show_alert=True)
        return
    
    # In real app, save to database
    # For now, just show confirmation
    
    await callback.answer("⭐ Added to wishlist", show_alert=False)

@router.callback_query(F.data.startswith("wishlist_del_"))
async def wishlist_del(callback: CallbackQuery):
    """
    Remove product from wishlist
    
    Extracts item ID and removes from wishlist
    """
    try:
        # Extract item ID from callback_data
        # Format: "wishlist_del_5" -> extract "5"
        item_id = int(callback.data.split("_")[2])
    except (ValueError, IndexError):
        await callback.answer("Invalid item", show_alert=True)
        return
    
    # In real app, delete from database
    # For now, just show confirmation
    
    await callback.answer("Removed from wishlist")
