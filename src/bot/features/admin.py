# ============================================
# FEATURE: Admin Panel
# ============================================
# Purpose: Admin controls for product management & customization
# Admins can add products, manage stock, and customize welcome message/image

# ===== IMPORTS =====
from aiogram import Router, F, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ForceReply
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from src.database.json_db import db
from src.config import settings
from src.logger import logger
import os

router = Router()

# ============================================
# ===== STATES =====
# ============================================
# FSM states for multi-step operations

class ProductStates(StatesGroup):
    """States for product creation wizard"""
    waiting_for_name = State()
    waiting_for_price = State()

class StockStates(StatesGroup):
    """States for stock upload"""
    waiting_for_keys = State()

class CustomizationStates(StatesGroup):
    """States for welcome message customization"""
    waiting_for_welcome_text = State()
    waiting_for_welcome_image = State()

# ============================================
# ===== MESSAGES SECTION =====
# ============================================

ADMIN_PANEL = "🔐 **Admin Panel**\n\nSelect an option to manage your store."
PRODUCT_MANAGEMENT = "📦 **Product Management**\nTotal Products: {count}"
PRODUCT_ADDED = "✅ Product **{name}** added!"
STOCK_ADDED = "✅ Added **{count}** keys to stock!"
STOCK_PROMPT = "🔑 **Send Stock Keys**\n\nSend each key on a new line."
PRODUCT_EDIT = "📦 **Editing: {name}**\n💲 Price: ${price}\n🔑 Stock Keys: {stock_count}"

# Customization messages
CUSTOMIZATION_MENU = "🎨 **Customize Welcome**\n\nChoose what to customize:"
WELCOME_TEXT_PROMPT = "📝 **Enter Welcome Message**\n\nYou can use:\n**bold** for bold\n_italic_ for italic\n`code` for code\n\nSend your custom welcome message:"
WELCOME_IMAGE_PROMPT = "🖼️ **Upload Welcome Image**\n\nSend an image file for the welcome screen.\n\nCurrent image: {current}"
WELCOME_TEXT_SAVED = "✅ Welcome message updated!"
WELCOME_IMAGE_SAVED = "✅ Welcome image updated!"
CURRENT_SETTINGS = "⚙️ **Current Settings**\n\nWelcome Text:\n{text}\n\nWelcome Image: {image}"

# ============================================
# ===== KEYBOARDS SECTION =====
# ============================================

def get_admin_main_keyboard() -> InlineKeyboardMarkup:
    """Build admin main menu keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📦 Manage Products", callback_data="admin_products")],
        [InlineKeyboardButton(text="🎨 Customize Welcome", callback_data="customize_welcome")],
        [InlineKeyboardButton(text="⚙️ View Settings", callback_data="view_settings")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="back_main")]
    ])

def get_admin_products_keyboard(products: list) -> InlineKeyboardMarkup:
    """Build products management keyboard"""
    buttons = [[InlineKeyboardButton(text="➕ Add Product", callback_data="add_product")]]
    
    for prod in products[:5]:
        buttons.append([InlineKeyboardButton(text=f"✏️ {prod['name']}", callback_data=f"edit_prod_{prod['id']}")])
    
    buttons.append([InlineKeyboardButton(text="⬅️ Back", callback_data="admin_panel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_product_edit_keyboard(prod_id: int) -> InlineKeyboardMarkup:
    """Build product edit keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔑 Add Stock", callback_data=f"add_stock_{prod_id}")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="admin_products")]
    ])

def get_customization_keyboard() -> InlineKeyboardMarkup:
    """Build customization menu keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Change Welcome Text", callback_data="set_welcome_text")],
        [InlineKeyboardButton(text="🖼️ Change Welcome Image", callback_data="set_welcome_image")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="admin_panel")]
    ])

# ============================================
# ===== HELPER FUNCTIONS =====
# ============================================

def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return (user_id in settings.ADMIN_IDS or 
            str(user_id) in db.settings.get("admin_ids", []))

# ============================================
# ===== HANDLERS SECTION =====
# ============================================

@router.message(Command("admin"))
async def admin_panel_command(message: Message):
    """Handle /admin command"""
    if not is_admin(message.from_user.id):
        return
    
    keyboard = get_admin_main_keyboard()
    await message.answer(ADMIN_PANEL, reply_markup=keyboard, parse_mode="Markdown")

@router.callback_query(F.data == "admin_panel")
async def admin_panel_callback(callback: CallbackQuery):
    """Show admin panel"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Authorized Personnel Only", show_alert=True)
        return
    
    keyboard = get_admin_main_keyboard()
    await callback.message.edit_text(ADMIN_PANEL, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()

# ============================================
# PRODUCT MANAGEMENT HANDLERS
# ============================================

@router.callback_query(F.data == "admin_products")
async def list_products(callback: CallbackQuery):
    """List all products"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Authorized Personnel Only", show_alert=True)
        return
    
    products = db.get_products()
    text = PRODUCT_MANAGEMENT.format(count=len(products))
    keyboard = get_admin_products_keyboard(products)
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "add_product")
async def start_add_product(callback: CallbackQuery, state: FSMContext):
    """Start adding product"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Authorized Personnel Only", show_alert=True)
        return
    
    await state.set_state(ProductStates.waiting_for_name)
    await callback.message.answer("📝 Enter the **Product Name**:", reply_markup=ForceReply(), parse_mode="Markdown")
    await callback.answer()

@router.message(ProductStates.waiting_for_name)
async def product_name_received(message: Message, state: FSMContext):
    """Receive product name"""
    if not is_admin(message.from_user.id):
        return
    
    await state.update_data(name=message.text)
    await state.set_state(ProductStates.waiting_for_price)
    await message.answer("💲 Enter the **Price (USD)** (e.g. 10.50):", parse_mode="Markdown")

@router.message(ProductStates.waiting_for_price)
async def product_price_received(message: Message, state: FSMContext):
    """Receive product price"""
    if not is_admin(message.from_user.id):
        return
    
    try:
        price = float(message.text)
    except ValueError:
        await message.answer("❌ Invalid price. Please enter a number like 10.99")
        return
    
    data = await state.get_data()
    
    new_prod = {
        "name": data['name'],
        "price": price,
        "category_id": 1,
        "description": "No description",
        "image_url": None,
        "stock_count": 0
    }
    
    prod_id = db.add_product(new_prod)
    await state.clear()
    
    keyboard = get_product_edit_keyboard(prod_id)
    await message.answer(PRODUCT_ADDED.format(name=data['name']), reply_markup=keyboard, parse_mode="Markdown")

@router.callback_query(F.data.startswith("edit_prod_"))
async def edit_product_menu(callback: CallbackQuery):
    """Edit product menu"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Authorized Personnel Only", show_alert=True)
        return
    
    try:
        prod_id = int(callback.data.split("_")[2])
    except (ValueError, IndexError):
        await callback.answer("Invalid product", show_alert=True)
        return
    
    product = db.get_product(prod_id)
    if not product:
        await callback.answer("Product not found", show_alert=True)
        return
    
    stock_count = db.get_stock_count(prod_id)
    text = PRODUCT_EDIT.format(name=product['name'], price=product['price'], stock_count=stock_count)
    
    keyboard = get_product_edit_keyboard(prod_id)
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data.startswith("add_stock_"))
async def start_add_stock(callback: CallbackQuery, state: FSMContext):
    """Start adding stock"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Authorized Personnel Only", show_alert=True)
        return
    
    try:
        prod_id = int(callback.data.split("_")[2])
    except (ValueError, IndexError):
        await callback.answer("Invalid product", show_alert=True)
        return
    
    await state.update_data(prod_id=prod_id)
    await state.set_state(StockStates.waiting_for_keys)
    
    await callback.message.answer(STOCK_PROMPT, reply_markup=ForceReply(), parse_mode="Markdown")
    await callback.answer()

@router.message(StockStates.waiting_for_keys)
async def receive_stock_keys(message: Message, state: FSMContext):
    """Receive stock keys"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Unauthorized")
        await state.clear()
        return
    
    data = await state.get_data()
    prod_id = data['prod_id']
    
    keys = [k.strip() for k in message.text.split('\n') if k.strip()]
    
    if keys:
        db.add_stock(prod_id, keys)
        await message.answer(STOCK_ADDED.format(count=len(keys)))
    else:
        await message.answer("❌ No valid keys found.")
    
    await state.clear()

# ============================================
# CUSTOMIZATION HANDLERS
# ============================================

@router.callback_query(F.data == "customize_welcome")
async def customize_welcome(callback: CallbackQuery):
    """Show customization menu"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Authorized Personnel Only", show_alert=True)
        return
    
    keyboard = get_customization_keyboard()
    await callback.message.edit_text(CUSTOMIZATION_MENU, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "set_welcome_text")
async def set_welcome_text(callback: CallbackQuery, state: FSMContext):
    """Start setting welcome text"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Authorized Personnel Only", show_alert=True)
        return
    
    await state.set_state(CustomizationStates.waiting_for_welcome_text)
    await callback.message.answer(WELCOME_TEXT_PROMPT, reply_markup=ForceReply(), parse_mode="Markdown")
    await callback.answer()

@router.message(CustomizationStates.waiting_for_welcome_text)
async def receive_welcome_text(message: Message, state: FSMContext):
    """Receive and save welcome text"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Unauthorized")
        await state.clear()
        return
    
    # Save custom welcome text to database
    db.settings["custom_welcome_text"] = message.text
    db.save_settings()
    
    await message.answer(WELCOME_TEXT_SAVED)
    await state.clear()

@router.callback_query(F.data == "set_welcome_image")
async def set_welcome_image(callback: CallbackQuery, state: FSMContext):
    """Start setting welcome image"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Authorized Personnel Only", show_alert=True)
        return
    
    current = db.settings.get("custom_welcome_image", "None")
    text = WELCOME_IMAGE_PROMPT.format(current=current)
    
    await state.set_state(CustomizationStates.waiting_for_welcome_image)
    await callback.message.answer(text, reply_markup=ForceReply())
    await callback.answer()

@router.message(CustomizationStates.waiting_for_welcome_image)
async def receive_welcome_image(message: Message, state: FSMContext):
    """Receive and save welcome image"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Unauthorized")
        await state.clear()
        return
    
    # Check if message has photo
    if message.photo:
        # Get the largest photo
        photo = message.photo[-1]
        file_id = photo.file_id
        
        # Save file_id to database
        db.settings["custom_welcome_image"] = file_id
        db.save_settings()
        
        await message.answer(WELCOME_IMAGE_SAVED)
    else:
        await message.answer("❌ Please send an image file")
    
    await state.clear()

@router.callback_query(F.data == "view_settings")
async def view_settings(callback: CallbackQuery):
    """View current settings"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Authorized Personnel Only", show_alert=True)
        return
    
    welcome_text = db.settings.get("custom_welcome_text", "Default welcome message")
    welcome_image = db.settings.get("custom_welcome_image", "None")
    
    text = CURRENT_SETTINGS.format(text=welcome_text[:100], image=welcome_image[:20] if welcome_image != "None" else "None")
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back", callback_data="admin_panel")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()
