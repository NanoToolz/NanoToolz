from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def admin_main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📦 Manage Products", callback_data="admin_products"),
            InlineKeyboardButton(text="📂 Manage Categories", callback_data="admin_categories")
        ],
        [
            InlineKeyboardButton(text="📊 Stock & Keys", callback_data="admin_stock"),
            InlineKeyboardButton(text="👥 Users & Credits", callback_data="admin_users")
        ],
        [
            InlineKeyboardButton(text="⚙️ Settings", callback_data="admin_settings"),
            InlineKeyboardButton(text="⬅️ Exit Admin", callback_data="back_main")
        ]
    ])

def admin_products_keyboard(products):
    keyboard = []
    # List products
    for p in products:
        keyboard.append([InlineKeyboardButton(
            text=f"✏️ {p['name']} (${p['price']})", 
            callback_data=f"edit_prod_{p['id']}"
        )])
        
    # Controls
    keyboard.append([InlineKeyboardButton(text="➕ Add New Product", callback_data="add_product")])
    keyboard.append([InlineKeyboardButton(text="⬅️ Back to Admin", callback_data="admin_panel")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def admin_product_edit_keyboard(product_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📝 Edit Name", callback_data=f"edit_p_name_{product_id}"),
            InlineKeyboardButton(text="💲 Edit Price", callback_data=f"edit_p_price_{product_id}")
        ],
        [
            InlineKeyboardButton(text="🖼️ Edit Image", callback_data=f"edit_p_image_{product_id}"),
            InlineKeyboardButton(text="🔑 Add Stock", callback_data=f"add_stock_{product_id}")
        ],
        [
            InlineKeyboardButton(text="🗑️ Delete Product", callback_data=f"del_prod_{product_id}"),
            InlineKeyboardButton(text="⬅️ Back", callback_data="admin_products")
        ]
    ])