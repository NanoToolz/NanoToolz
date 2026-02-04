from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from src.database import db

router = Router()

CATALOG_TITLE = "Catalog Categories\nSelect a category to browse:"
NO_CATEGORIES = "No categories available"

PRODUCT_DETAIL_TEMPLATE = (
    "{name}\n\n"
    "{description}\n\n"
    "Price: ${price}\n"
    "Status: {status}\n"
)


class SearchStates(StatesGroup):
    waiting_for_query = State()


def get_categories_keyboard(categories: list) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(
            text=f"{cat['emoji']} {cat['name']}",
            callback_data=f"cat_{cat['id']}"
        )]
        for cat in categories
    ]
    buttons.append([InlineKeyboardButton(text="Search Products", callback_data="search_products")])
    buttons.append([InlineKeyboardButton(text="Back", callback_data="back_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_products_keyboard(products: list, cat_id: int) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(
            text=f"{p['name']} - ${p['price']}",
            callback_data=f"prod_{p['id']}"
        )]
        for p in products
    ]
    buttons.append([InlineKeyboardButton(text="Back", callback_data="catalog_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_product_detail_keyboard(prod_id: int, cat_id: int, in_wishlist: bool = False) -> InlineKeyboardMarkup:
    wishlist_btn = InlineKeyboardButton(
        text="Remove from Wishlist" if in_wishlist else "Add to Wishlist",
        callback_data=f"wishlist_toggle_{prod_id}"
    )
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Add to Cart", callback_data=f"add_cart_{prod_id}")],
        [wishlist_btn],
        [InlineKeyboardButton(text="Back", callback_data=f"cat_{cat_id}")]
    ])


@router.callback_query(F.data == "catalog_main")
async def show_categories(callback: CallbackQuery):
    categories = db.get_categories()

    if not categories:
        await callback.answer(NO_CATEGORIES, show_alert=True)
        return

    keyboard = get_categories_keyboard(categories)

    try:
        await callback.message.edit_text(CATALOG_TITLE, reply_markup=keyboard, parse_mode="Markdown")
    except Exception:
        await callback.message.delete()
        await callback.message.answer(CATALOG_TITLE, reply_markup=keyboard, parse_mode="Markdown")

    await callback.answer()


@router.callback_query(F.data.startswith("cat_"))
async def show_products(callback: CallbackQuery):
    try:
        cat_id = int(callback.data.split("_")[1])
    except (ValueError, IndexError):
        await callback.answer("Invalid category", show_alert=True)
        return

    category = db.get_category(cat_id)
    if not category:
        await callback.answer("Category not found", show_alert=True)
        return

    products = db.get_products(category_id=cat_id)

    if not products:
        text = f"No products found in {category['name']}"
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Back", callback_data="catalog_main")]]
        )
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
        await callback.answer()
        return

    keyboard = get_products_keyboard(products, cat_id)

    await callback.message.edit_text(
        f"{category['name']}\nSelect a product:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

    await callback.answer()


@router.callback_query(F.data.startswith("prod_"))
async def show_product_detail(callback: CallbackQuery):
    try:
        prod_id = int(callback.data.split("_")[1])
    except (ValueError, IndexError):
        await callback.answer("Invalid product", show_alert=True)
        return

    product = db.get_product(prod_id)

    if not product:
        await callback.answer("Product not found", show_alert=True)
        return

    stock = db.get_stock_count(prod_id)
    stock_status = f"In Stock ({stock})" if stock > 0 else "Out of Stock"

    user_id = callback.from_user.id
    in_wishlist = db.is_in_wishlist(user_id, prod_id)

    text = PRODUCT_DETAIL_TEMPLATE.format(
        name=product['name'],
        description=product.get('description', 'No description'),
        price=product['price'],
        status=stock_status
    )

    keyboard = get_product_detail_keyboard(prod_id, product['category_id'], in_wishlist)

    image_url = product.get("image_url")
    if not image_url:
        image_url = "https://images.pexels.com/photos/5632402/pexels-photo-5632402.jpeg?auto=compress&cs=tinysrgb&w=400"

    try:
        await callback.message.delete()
        await callback.message.answer_photo(
            photo=image_url,
            caption=text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
    except Exception:
        try:
            await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
        except Exception:
            await callback.message.answer(text, reply_markup=keyboard, parse_mode="Markdown")

    await callback.answer()


@router.callback_query(F.data == "search_products")
async def start_search(callback: CallbackQuery, state: FSMContext):
    await state.set_state(SearchStates.waiting_for_query)
    await callback.message.answer("Enter product name to search:")
    await callback.answer()


@router.message(SearchStates.waiting_for_query)
async def process_search(message: Message, state: FSMContext):
    query = message.text.strip()
    await state.clear()

    if len(query) < 2:
        await message.answer("Search query too short. Please enter at least 2 characters.")
        return

    products = db.search_products(query)

    if not products:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Back to Catalog", callback_data="catalog_main")]]
        )
        await message.answer(f"No products found for '{query}'", reply_markup=keyboard)
        return

    buttons = [
        [InlineKeyboardButton(
            text=f"{p['name']} - ${p['price']}",
            callback_data=f"prod_{p['id']}"
        )]
        for p in products[:10]
    ]
    buttons.append([InlineKeyboardButton(text="Back to Catalog", callback_data="catalog_main")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await message.answer(f"Search results for '{query}':", reply_markup=keyboard)


@router.callback_query(F.data.startswith("wishlist_toggle_"))
async def toggle_wishlist(callback: CallbackQuery):
    try:
        prod_id = int(callback.data.split("_")[2])
    except (ValueError, IndexError):
        await callback.answer("Invalid product", show_alert=True)
        return

    user_id = callback.from_user.id

    if db.is_in_wishlist(user_id, prod_id):
        db.remove_from_wishlist(user_id, prod_id)
        await callback.answer("Removed from wishlist")
    else:
        db.add_to_wishlist(user_id, prod_id)
        await callback.answer("Added to wishlist")

    product = db.get_product(prod_id)
    if product:
        in_wishlist = db.is_in_wishlist(user_id, prod_id)
        keyboard = get_product_detail_keyboard(prod_id, product['category_id'], in_wishlist)

        stock = db.get_stock_count(prod_id)
        stock_status = f"In Stock ({stock})" if stock > 0 else "Out of Stock"

        text = PRODUCT_DETAIL_TEMPLATE.format(
            name=product['name'],
            description=product.get('description', 'No description'),
            price=product['price'],
            status=stock_status
        )

        try:
            await callback.message.edit_caption(caption=text, reply_markup=keyboard, parse_mode="Markdown")
        except Exception:
            pass
