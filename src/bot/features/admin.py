from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ForceReply
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from src.database import db
from src.config import settings

router = Router()


class ProductStates(StatesGroup):
    waiting_for_category = State()
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_price = State()
    waiting_for_image = State()


class CategoryStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_emoji = State()


class StockStates(StatesGroup):
    waiting_for_keys = State()


class CouponStates(StatesGroup):
    waiting_for_code = State()
    waiting_for_discount = State()
    waiting_for_max_uses = State()


class CustomizationStates(StatesGroup):
    waiting_for_welcome_text = State()
    waiting_for_welcome_image = State()


def is_admin(user_id: int) -> bool:
    return user_id in settings.ADMIN_IDS


def get_admin_main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Dashboard", callback_data="admin_dashboard")],
        [InlineKeyboardButton(text="Manage Categories", callback_data="admin_categories")],
        [InlineKeyboardButton(text="Manage Products", callback_data="admin_products")],
        [InlineKeyboardButton(text="Manage Coupons", callback_data="admin_coupons")],
        [InlineKeyboardButton(text="Support Tickets", callback_data="admin_tickets")],
        [InlineKeyboardButton(text="Customize Welcome", callback_data="customize_welcome")],
        [InlineKeyboardButton(text="Back", callback_data="back_main")]
    ])


@router.message(Command("admin"))
async def admin_panel_command(message: Message):
    if not is_admin(message.from_user.id):
        return

    keyboard = get_admin_main_keyboard()
    await message.answer("Admin Panel\n\nSelect an option to manage your store.", reply_markup=keyboard, parse_mode="Markdown")


@router.callback_query(F.data == "admin_panel")
async def admin_panel_callback(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Authorized Personnel Only", show_alert=True)
        return

    keyboard = get_admin_main_keyboard()
    try:
        await callback.message.edit_text("Admin Panel\n\nSelect an option to manage your store.", reply_markup=keyboard, parse_mode="Markdown")
    except Exception:
        await callback.message.delete()
        await callback.message.answer("Admin Panel\n\nSelect an option to manage your store.", reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "admin_dashboard")
async def admin_dashboard(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Authorized Personnel Only", show_alert=True)
        return

    stats = db.get_stats()

    text = (
        "Dashboard\n\n"
        f"Total Users: {stats['total_users']}\n"
        f"Total Orders: {stats['total_orders']}\n"
        f"Total Revenue: ${stats['total_revenue']:.2f}\n"
        f"Active Products: {stats['total_products']}\n"
        f"Stock Available: {stats['total_stock']}\n"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Refresh", callback_data="admin_dashboard")],
        [InlineKeyboardButton(text="Back", callback_data="admin_panel")]
    ])

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "admin_categories")
async def admin_categories(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Authorized Personnel Only", show_alert=True)
        return

    categories = db.get_categories()

    buttons = [[InlineKeyboardButton(text="+ Add Category", callback_data="add_category")]]

    for cat in categories:
        buttons.append([InlineKeyboardButton(
            text=f"{cat['emoji']} {cat['name']}",
            callback_data=f"edit_cat_{cat['id']}"
        )])

    buttons.append([InlineKeyboardButton(text="Back", callback_data="admin_panel")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await callback.message.edit_text(f"Categories ({len(categories)})\n\nSelect to edit or add new:", reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "add_category")
async def start_add_category(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Authorized Personnel Only", show_alert=True)
        return

    await state.set_state(CategoryStates.waiting_for_name)
    await callback.message.answer("Enter category name:", reply_markup=ForceReply())
    await callback.answer()


@router.message(CategoryStates.waiting_for_name)
async def category_name_received(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await state.clear()
        return

    await state.update_data(name=message.text)
    await state.set_state(CategoryStates.waiting_for_emoji)
    await message.answer("Enter category emoji (e.g. ):", reply_markup=ForceReply())


@router.message(CategoryStates.waiting_for_emoji)
async def category_emoji_received(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await state.clear()
        return

    data = await state.get_data()
    emoji = message.text.strip() or ""

    db.create_category(data['name'], emoji)
    await state.clear()

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Back to Categories", callback_data="admin_categories")]
    ])
    await message.answer(f"Category '{data['name']}' created!", reply_markup=keyboard)


@router.callback_query(F.data == "admin_products")
async def list_products(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Authorized Personnel Only", show_alert=True)
        return

    products = db.get_products()

    buttons = [[InlineKeyboardButton(text="+ Add Product", callback_data="add_product")]]

    for prod in products[:10]:
        stock = db.get_stock_count(prod['id'])
        buttons.append([InlineKeyboardButton(
            text=f"{prod['name']} (${prod['price']}) [{stock}]",
            callback_data=f"edit_prod_{prod['id']}"
        )])

    buttons.append([InlineKeyboardButton(text="Back", callback_data="admin_panel")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await callback.message.edit_text(f"Products ({len(products)})\n\nSelect to edit or add new:", reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "add_product")
async def start_add_product(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Authorized Personnel Only", show_alert=True)
        return

    categories = db.get_categories()

    if not categories:
        await callback.answer("Create a category first!", show_alert=True)
        return

    buttons = []
    for cat in categories:
        buttons.append([InlineKeyboardButton(
            text=f"{cat['emoji']} {cat['name']}",
            callback_data=f"new_prod_cat_{cat['id']}"
        )])
    buttons.append([InlineKeyboardButton(text="Cancel", callback_data="admin_products")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await callback.message.edit_text("Select category for new product:", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("new_prod_cat_"))
async def select_product_category(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Authorized Personnel Only", show_alert=True)
        return

    try:
        cat_id = int(callback.data.split("_")[3])
    except (ValueError, IndexError):
        await callback.answer("Invalid category", show_alert=True)
        return

    await state.update_data(category_id=cat_id)
    await state.set_state(ProductStates.waiting_for_name)
    await callback.message.answer("Enter product name:", reply_markup=ForceReply())
    await callback.answer()


@router.message(ProductStates.waiting_for_name)
async def product_name_received(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await state.clear()
        return

    await state.update_data(name=message.text)
    await state.set_state(ProductStates.waiting_for_description)
    await message.answer("Enter product description:", reply_markup=ForceReply())


@router.message(ProductStates.waiting_for_description)
async def product_desc_received(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await state.clear()
        return

    await state.update_data(description=message.text)
    await state.set_state(ProductStates.waiting_for_price)
    await message.answer("Enter price (USD):", reply_markup=ForceReply())


@router.message(ProductStates.waiting_for_price)
async def product_price_received(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await state.clear()
        return

    try:
        price = float(message.text)
    except ValueError:
        await message.answer("Invalid price. Please enter a number like 10.99")
        return

    data = await state.get_data()

    product = db.create_product(
        category_id=data['category_id'],
        name=data['name'],
        price=price,
        description=data['description']
    )

    await state.clear()

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Add Stock", callback_data=f"add_stock_{product['id']}")],
        [InlineKeyboardButton(text="Back to Products", callback_data="admin_products")]
    ])

    await message.answer(f"Product '{data['name']}' created!\n\nNow add stock keys.", reply_markup=keyboard)


@router.callback_query(F.data.startswith("edit_prod_"))
async def edit_product_menu(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Authorized Personnel Only", show_alert=True)
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

    text = (
        f"Editing: {product['name']}\n\n"
        f"Price: ${product['price']}\n"
        f"Stock: {stock_count} keys\n"
        f"Description: {product.get('description', 'None')[:100]}\n"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Add Stock", callback_data=f"add_stock_{prod_id}")],
        [InlineKeyboardButton(text="Delete Product", callback_data=f"del_prod_{prod_id}")],
        [InlineKeyboardButton(text="Back", callback_data="admin_products")]
    ])

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data.startswith("del_prod_"))
async def delete_product(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Authorized Personnel Only", show_alert=True)
        return

    try:
        prod_id = int(callback.data.split("_")[2])
    except (ValueError, IndexError):
        await callback.answer("Invalid product", show_alert=True)
        return

    db.delete_product(prod_id)
    await callback.answer("Product deleted")

    products = db.get_products()
    buttons = [[InlineKeyboardButton(text="+ Add Product", callback_data="add_product")]]
    for prod in products[:10]:
        stock = db.get_stock_count(prod['id'])
        buttons.append([InlineKeyboardButton(
            text=f"{prod['name']} (${prod['price']}) [{stock}]",
            callback_data=f"edit_prod_{prod['id']}"
        )])
    buttons.append([InlineKeyboardButton(text="Back", callback_data="admin_panel")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await callback.message.edit_text(f"Products ({len(products)})", reply_markup=keyboard, parse_mode="Markdown")


@router.callback_query(F.data.startswith("add_stock_"))
async def start_add_stock(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Authorized Personnel Only", show_alert=True)
        return

    try:
        prod_id = int(callback.data.split("_")[2])
    except (ValueError, IndexError):
        await callback.answer("Invalid product", show_alert=True)
        return

    await state.update_data(prod_id=prod_id)
    await state.set_state(StockStates.waiting_for_keys)

    await callback.message.answer("Send stock keys (one per line):", reply_markup=ForceReply())
    await callback.answer()


@router.message(StockStates.waiting_for_keys)
async def receive_stock_keys(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await state.clear()
        return

    data = await state.get_data()
    prod_id = data['prod_id']

    keys = [k.strip() for k in message.text.split('\n') if k.strip()]

    if keys:
        count = db.add_stock(prod_id, keys)
        await message.answer(f"Added {count} keys to stock!")
    else:
        await message.answer("No valid keys found.")

    await state.clear()

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Add More", callback_data=f"add_stock_{prod_id}")],
        [InlineKeyboardButton(text="Back to Products", callback_data="admin_products")]
    ])
    await message.answer("What next?", reply_markup=keyboard)


@router.callback_query(F.data == "admin_coupons")
async def admin_coupons(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Authorized Personnel Only", show_alert=True)
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="+ Create Coupon", callback_data="create_coupon")],
        [InlineKeyboardButton(text="Back", callback_data="admin_panel")]
    ])

    await callback.message.edit_text("Coupon Management\n\nCreate discount codes for customers.", reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "create_coupon")
async def start_create_coupon(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Authorized Personnel Only", show_alert=True)
        return

    await state.set_state(CouponStates.waiting_for_code)
    await callback.message.answer("Enter coupon code (e.g., SAVE20):", reply_markup=ForceReply())
    await callback.answer()


@router.message(CouponStates.waiting_for_code)
async def coupon_code_received(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await state.clear()
        return

    await state.update_data(code=message.text.upper())
    await state.set_state(CouponStates.waiting_for_discount)
    await message.answer("Enter discount percentage (e.g., 20 for 20% off):", reply_markup=ForceReply())


@router.message(CouponStates.waiting_for_discount)
async def coupon_discount_received(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await state.clear()
        return

    try:
        discount = int(message.text)
    except ValueError:
        await message.answer("Invalid discount. Enter a number like 20")
        return

    data = await state.get_data()

    db.create_coupon(data['code'], discount_percent=discount)
    await state.clear()

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Create Another", callback_data="create_coupon")],
        [InlineKeyboardButton(text="Back", callback_data="admin_coupons")]
    ])

    await message.answer(f"Coupon '{data['code']}' created with {discount}% discount!", reply_markup=keyboard)


@router.callback_query(F.data == "admin_tickets")
async def admin_tickets(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Authorized Personnel Only", show_alert=True)
        return

    tickets = db.get_open_tickets()

    if not tickets:
        text = "No open support tickets."
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Refresh", callback_data="admin_tickets")],
            [InlineKeyboardButton(text="Back", callback_data="admin_panel")]
        ])
    else:
        text = f"Open Tickets ({len(tickets)})\n\n"
        buttons = []

        for ticket in tickets[:10]:
            user = ticket.get('users', {})
            username = user.get('username') or user.get('first_name') or 'Unknown'
            buttons.append([InlineKeyboardButton(
                text=f"#{ticket['id']} - {ticket['subject'][:20]} (@{username})",
                callback_data=f"view_ticket_{ticket['id']}"
            )])

        buttons.append([InlineKeyboardButton(text="Refresh", callback_data="admin_tickets")])
        buttons.append([InlineKeyboardButton(text="Back", callback_data="admin_panel")])
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data.startswith("view_ticket_"))
async def view_ticket_admin(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Authorized Personnel Only", show_alert=True)
        return

    try:
        ticket_id = int(callback.data.split("_")[2])
    except (ValueError, IndexError):
        await callback.answer("Invalid ticket", show_alert=True)
        return

    ticket = db.get_ticket(ticket_id)
    if not ticket:
        await callback.answer("Ticket not found", show_alert=True)
        return

    text = f"Ticket #{ticket['id']}\n\nSubject: {ticket['subject']}\nStatus: {ticket['status']}\n\nMessages:\n"

    messages = ticket.get('ticket_messages', [])
    for msg in messages[-5:]:
        sender = "Admin" if msg['is_admin'] else "User"
        text += f"\n[{sender}]: {msg['message'][:100]}"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Reply", callback_data=f"reply_ticket_{ticket_id}")],
        [InlineKeyboardButton(text="Close Ticket", callback_data=f"close_ticket_{ticket_id}")],
        [InlineKeyboardButton(text="Back", callback_data="admin_tickets")]
    ])

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data.startswith("close_ticket_"))
async def close_ticket(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Authorized Personnel Only", show_alert=True)
        return

    try:
        ticket_id = int(callback.data.split("_")[2])
    except (ValueError, IndexError):
        await callback.answer("Invalid ticket", show_alert=True)
        return

    db.update_ticket_status(ticket_id, "closed")
    await callback.answer("Ticket closed")

    tickets = db.get_open_tickets()
    text = f"Open Tickets ({len(tickets)})" if tickets else "No open tickets"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Refresh", callback_data="admin_tickets")],
        [InlineKeyboardButton(text="Back", callback_data="admin_panel")]
    ])

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")


@router.callback_query(F.data == "customize_welcome")
async def customize_welcome(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Authorized Personnel Only", show_alert=True)
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Change Welcome Text", callback_data="set_welcome_text")],
        [InlineKeyboardButton(text="Change Welcome Image", callback_data="set_welcome_image")],
        [InlineKeyboardButton(text="Back", callback_data="admin_panel")]
    ])

    await callback.message.edit_text("Customize Welcome\n\nChoose what to customize:", reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "set_welcome_text")
async def set_welcome_text(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Authorized Personnel Only", show_alert=True)
        return

    await state.set_state(CustomizationStates.waiting_for_welcome_text)
    await callback.message.answer("Enter new welcome message:\n\nUse {first_name} and {user_id} as placeholders.", reply_markup=ForceReply())
    await callback.answer()


@router.message(CustomizationStates.waiting_for_welcome_text)
async def receive_welcome_text(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await state.clear()
        return

    db.set_setting("welcome_message", message.text)
    await state.clear()
    await message.answer("Welcome message updated!")


@router.callback_query(F.data == "set_welcome_image")
async def set_welcome_image(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Authorized Personnel Only", show_alert=True)
        return

    await state.set_state(CustomizationStates.waiting_for_welcome_image)
    await callback.message.answer("Send an image for the welcome screen:", reply_markup=ForceReply())
    await callback.answer()


@router.message(CustomizationStates.waiting_for_welcome_image)
async def receive_welcome_image(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await state.clear()
        return

    if message.photo:
        photo = message.photo[-1]
        db.set_setting("welcome_image", photo.file_id)
        await message.answer("Welcome image updated!")
    else:
        await message.answer("Please send an image file")

    await state.clear()
