from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ForceReply
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from src.database.json_db import db
from src.config import settings
from src.bot.features.admin.keyboards import (
    admin_main_keyboard,
    admin_products_keyboard,
    admin_product_edit_keyboard
)

router = Router()

class ProductStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_price = State()
    waiting_for_category = State()
    waiting_for_stock = State()

def is_admin(user_id: int) -> bool:
    # Check both config and runtime settings
    return (user_id in settings.ADMIN_IDS or 
            str(user_id) in db.settings.get("admin_ids", []))

@router.message(Command("admin"))
async def admin_panel_command(message: Message):
    if not is_admin(message.from_user.id):
        return
    
    await message.answer(
        "🔐 **Admin Panel**\n\nSelect an option to manage your store.",
        reply_markup=admin_main_keyboard(),
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "admin_panel")
async def admin_panel_callback(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    
    await callback.message.edit_text(
        "🔐 **Admin Panel**\n\nSelect an option to manage your store.",
        reply_markup=admin_main_keyboard(),
        parse_mode="Markdown"
    )

# --- Product Management ---
@router.callback_query(F.data == "admin_products")
async def list_products(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Authorized Personnel Only", show_alert=True)
        return
        
    products = db.get_products()
    await callback.message.edit_text(
        f"📦 **Product Management**\nTotal Products: {len(products)}",
        reply_markup=admin_products_keyboard(products),
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "add_product")
async def start_add_product(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Authorized Personnel Only", show_alert=True)
        return
        
    await state.set_state(ProductStates.waiting_for_name)
    await callback.message.answer(
        "📝 Enter the **Product Name**:",
        reply_markup=ForceReply()
    )
    await callback.answer()

@router.message(ProductStates.waiting_for_name)
async def product_name_received(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id): return
    await state.update_data(name=message.text)
    await state.set_state(ProductStates.waiting_for_price)
    await message.answer("💲 Enter the **Price (USD)** (e.g. 10.50):")

@router.message(ProductStates.waiting_for_price)
async def product_price_received(message: Message, state: FSMContext):
    try:
        price = float(message.text)
    except ValueError:
        await message.answer("❌ Invalid price. Please enter a number like 10.99")
        return

    data = await state.get_data()
    # Create product with default category 1
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
    
    await message.answer(
        f"✅ Product **{data['name']}** added!",
        reply_markup=admin_product_edit_keyboard(prod_id),
        parse_mode="Markdown"
    )

@router.callback_query(F.data.startswith("edit_prod_"))
async def edit_product_menu(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Authorized Personnel Only", show_alert=True)
        return

    prod_id = int(callback.data.split("_")[2])
    product = db.get_product(prod_id)
    
    if not product:
        await callback.answer("Product not found")
        return

    stock_count = db.get_stock_count(prod_id)
    text = (
        f"📦 **Editing: {product['name']}**\n"
        f"💲 Price: ${product['price']}\n"
        f"🔑 Stock Keys: {stock_count}"
    )
    
    await callback.message.edit_text(
        text, 
        reply_markup=admin_product_edit_keyboard(prod_id),
        parse_mode="Markdown"
    )

# --- Stock Logic ---
class StockStates(StatesGroup):
    waiting_for_keys = State()

@router.callback_query(F.data.startswith("add_stock_"))
async def start_add_stock(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Authorized Personnel Only", show_alert=True)
        return

    prod_id = int(callback.data.split("_")[2])
    await state.update_data(prod_id=prod_id)
    await state.set_state(StockStates.waiting_for_keys)
    
    await callback.message.answer(
        "🔑 **Send Stock Keys**\n\n"
        "Send each key on a new line, or upload a .txt file.",
        reply_markup=ForceReply(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.message(StockStates.waiting_for_keys)
async def receive_stock_keys(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id): return
    
    data = await state.get_data()
    prod_id = data['prod_id']
    
    keys = []
    if message.document:
        # Handle file upload logic here (omitted for brevity, requires bot download)
        await message.answer("⚠️ File upload not fully implemented yet. Send text.")
        return
    elif message.text:
        keys = [k.strip() for k in message.text.split('\n') if k.strip()]
        
    if keys:
        db.add_stock(prod_id, keys)
        await message.answer(f"✅ Added **{len(keys)}** keys to stock!")
    else:
        await message.answer("❌ No valid keys found.")
        
    await state.clear()