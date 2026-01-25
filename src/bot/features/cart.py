# ============================================
# FEATURE: Shopping Cart
# ============================================
# Purpose: Manage user's shopping cart
# Users can add, remove, and modify items in cart

# ===== IMPORTS =====
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from src.database.json_db import db

# Create router instance
router = Router()

# ============================================
# ===== MESSAGES SECTION =====
# ============================================
# All text messages for cart feature

# Message shown when cart is empty
EMPTY_CART = "🛒 **Your Cart is Empty**\n\nBrowse our catalog to add items."

# Title for cart display
CART_TITLE = "🛒 **Your Shopping Cart**\n\n"

# Template for each item in cart
# {name} = product name, {qty} = quantity, {price} = unit price, {subtotal} = total for item
CART_ITEM_TEMPLATE = "▪️ **{name}**\n   {qty} x ${price} = ${subtotal:.2f}\n"

# Template for cart total
# {total} = total price of all items
CART_TOTAL = "\n💰 **Total: ${total:.2f}**"

# ============================================
# ===== KEYBOARDS SECTION =====
# ============================================
# All button layouts for cart feature

def get_empty_cart_keyboard() -> InlineKeyboardMarkup:
    """
    Build keyboard for empty cart
    
    Returns:
        Keyboard with "Browse Catalog" and "Back" buttons
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🛍️ Browse Catalog", callback_data="catalog_main")],
            [InlineKeyboardButton(text="⬅️ Back", callback_data="back_main")]
        ]
    )

def get_cart_keyboard(cart_items: dict) -> InlineKeyboardMarkup:
    """
    Build keyboard for cart with quantity controls
    
    Args:
        cart_items: Dictionary of {product_id: quantity}
    
    Returns:
        Keyboard with quantity controls and checkout button
    """
    buttons = []
    
    # For each item in cart, create quantity control buttons
    for pid_str, qty in cart_items.items():
        # Create row with: Decrease, Quantity, Increase, Delete buttons
        buttons.append([
            InlineKeyboardButton(text="➖", callback_data=f"cart_dec_{pid_str}"),  # Decrease qty
            InlineKeyboardButton(text=f"{qty}", callback_data="noop"),  # Show current qty (no action)
            InlineKeyboardButton(text="➕", callback_data=f"cart_inc_{pid_str}"),  # Increase qty
            InlineKeyboardButton(text="🗑️", callback_data=f"cart_rem_{pid_str}")   # Delete item
        ])
    
    # Add checkout button
    buttons.append([InlineKeyboardButton(text="✅ Checkout", callback_data="checkout_start")])
    
    # Add back button
    buttons.append([InlineKeyboardButton(text="⬅️ Back", callback_data="back_main")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# ============================================
# ===== HANDLERS SECTION =====
# ============================================
# All handlers for cart feature

@router.callback_query(F.data == "cart_view")
async def view_cart(callback: CallbackQuery):
    """
    Display shopping cart
    
    This handler shows all items in user's cart with quantity controls
    """
    # Get user ID from callback
    user_id = callback.from_user.id
    
    # Get user data from database
    user = db.get_user(user_id)
    
    # Get cart items (dictionary of product_id: quantity)
    cart = user.get("cart", {})
    
    # Check if cart is empty
    if not cart:
        # Show empty cart message
        keyboard = get_empty_cart_keyboard()
        await callback.message.edit_text(EMPTY_CART, reply_markup=keyboard, parse_mode="Markdown")
        await callback.answer()
        return
    
    # Build cart display text
    total_price = 0
    text = CART_TITLE
    
    # Loop through each item in cart
    for pid_str, qty in cart.items():
        # Get product details from database
        product = db.get_product(int(pid_str))
        
        # Skip if product not found
        if not product:
            continue
        
        # Calculate subtotal for this item
        subtotal = product['price'] * qty
        total_price += subtotal
        
        # Add item to display text
        text += CART_ITEM_TEMPLATE.format(
            name=product['name'],
            qty=qty,
            price=product['price'],
            subtotal=subtotal
        )
    
    # Add total price to text
    text += CART_TOTAL.format(total=total_price)
    
    # Build keyboard with quantity controls
    keyboard = get_cart_keyboard(cart)
    
    # Edit message to show cart
    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    
    await callback.answer()

@router.callback_query(F.data.startswith("cart_inc_"))
async def increase_cart_item(callback: CallbackQuery):
    """
    Increase item quantity in cart
    
    This handler runs when user clicks the ➕ button
    """
    # Extract product ID from callback_data
    # Format: "cart_inc_42" -> extract "42"
    pid_str = callback.data.split("_")[2]
    
    # Get user ID
    user_id = callback.from_user.id
    
    # Get user data
    user = db.get_user(user_id)
    cart = user.get("cart", {})
    
    # Increase quantity if item exists in cart
    if pid_str in cart:
        cart[pid_str] += 1
        # Save updated cart to database
        db.update_user(user_id, {"cart": cart})
    
    # Refresh cart display
    await view_cart(callback)

@router.callback_query(F.data.startswith("cart_dec_"))
async def decrease_cart_item(callback: CallbackQuery):
    """
    Decrease item quantity in cart
    
    This handler runs when user clicks the ➖ button
    If quantity reaches 0, item is removed from cart
    """
    # Extract product ID from callback_data
    pid_str = callback.data.split("_")[2]
    
    # Get user ID
    user_id = callback.from_user.id
    
    # Get user data
    user = db.get_user(user_id)
    cart = user.get("cart", {})
    
    # Decrease quantity if item exists
    if pid_str in cart:
        if cart[pid_str] > 1:
            # If quantity > 1, just decrease it
            cart[pid_str] -= 1
        else:
            # If quantity = 1, remove item from cart
            del cart[pid_str]
        
        # Save updated cart to database
        db.update_user(user_id, {"cart": cart})
    
    # Refresh cart display
    await view_cart(callback)

@router.callback_query(F.data.startswith("cart_rem_"))
async def remove_cart_item(callback: CallbackQuery):
    """
    Remove item from cart completely
    
    This handler runs when user clicks the 🗑️ button
    """
    # Extract product ID from callback_data
    pid_str = callback.data.split("_")[2]
    
    # Get user ID
    user_id = callback.from_user.id
    
    # Get user data
    user = db.get_user(user_id)
    cart = user.get("cart", {})
    
    # Remove item if it exists in cart
    if pid_str in cart:
        del cart[pid_str]
        # Save updated cart to database
        db.update_user(user_id, {"cart": cart})
    
    # Show confirmation message
    await callback.answer("Item removed")
    
    # Refresh cart display
    await view_cart(callback)

@router.callback_query(F.data.startswith("add_cart_"))
async def add_to_cart(callback: CallbackQuery):
    """
    Add product to cart
    
    This handler runs when user clicks "Add to Cart" button on product detail
    """
    try:
        # Extract product ID from callback_data
        # Format: "add_cart_42" -> extract "42"
        prod_id = int(callback.data.split("_")[2])
    except (IndexError, ValueError):
        # Show error if product ID is invalid
        await callback.answer("❌ Invalid product!", show_alert=True)
        return
    
    # Get user ID
    user_id = callback.from_user.id
    
    # Get user data
    user = db.get_user(user_id)
    cart = user.get("cart", {})
    
    # Check if product is in stock
    if db.get_stock_count(prod_id) <= 0:
        # Show error if out of stock
        await callback.answer("❌ Out of Stock!", show_alert=True)
        return
    
    # Add product to cart
    pid_str = str(prod_id)
    
    # Get current quantity (0 if not in cart)
    current_qty = cart.get(pid_str, 0)
    
    # Increase quantity by 1
    cart[pid_str] = current_qty + 1
    
    # Save updated cart to database
    db.update_user(user_id, {"cart": cart})
    
    # Show success message
    await callback.answer("✅ Added to cart!", show_alert=False)
