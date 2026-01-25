from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from src.database.json_db import db

router = Router()

@router.callback_query(F.data == "catalog_main")
async def show_categories(callback: CallbackQuery):
    categories = db.get_categories()
    
    if not categories:
        await callback.answer("No categories available", show_alert=True)
        return
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=f"{cat['emoji']} {cat['name']}",
                callback_data=f"cat_{cat['id']}"
            )]
            for cat in categories
        ] + [
            [InlineKeyboardButton(text="⬅️ Back", callback_data="back_main")]
        ]
    )
    
    await callback.message.edit_text(
        "📚 **Catalog Categories**\nSelect a category to browse:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("cat_"))
async def show_products(callback: CallbackQuery):
    cat_id = int(callback.data.split("_")[1])
    category = db.get_category(cat_id)
    products = db.get_products(category_id=cat_id)
    
    if not products:
        text = f"🚫 No products found in **{category['name']}**"
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="⬅️ Back", callback_data="catalog_main")]]
        )
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
        return
    
    buttons = []
    for p in products:
        buttons.append([InlineKeyboardButton(
            text=f"📦 {p['name']} - ${p['price']}",
            callback_data=f"prod_{p['id']}"
        )])
        
    buttons.append([InlineKeyboardButton(text="⬅️ Back", callback_data="catalog_main")])
    
    await callback.message.edit_text(
        f"📂 **{category['name']}**\nSelect a product:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("prod_"))
async def show_product_detail(callback: CallbackQuery):
    prod_id = int(callback.data.split("_")[1])
    product = db.get_product(prod_id)
    
    if not product:
        await callback.answer("Product not found")
        return
        
    stock = db.get_stock_count(prod_id)
    stock_status = f"✅ In Stock ({stock})" if stock > 0 else "❌ Out of Stock"
    
    text = (
        f"📦 **{product['name']}**\n\n"
        f"📝 {product.get('description', 'No description')}\n\n"
        f"� Price: **${product['price']}**\n"
        f"� Status: {stock_status}\n"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Add to Cart", callback_data=f"add_cart_{prod_id}")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data=f"cat_{product['category_id']}")]
    ])
    
    # Placeholder Image Logic
    image_url = product.get("image_url")
    if not image_url:
        image_url = "https://via.placeholder.com/300x200.png?text=NanoToolz"
        
    try:
        # Check if message has media to edit, else send new media
        # Since we are editing text messages usually, we might need delete + send photo
        # But for smooth UX, let's try input media if previous was photo
        # For now, let's just stick to edit_text or delete/send
        await callback.message.delete()
        await callback.message.answer_photo(
            photo=image_url,
            caption=text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
    except Exception:
        # Fallback
        await callback.message.answer(text, reply_markup=keyboard, parse_mode="Markdown")
        
    await callback.answer()