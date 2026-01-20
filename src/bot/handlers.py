import logging
from aiogram import Dispatcher, Router, types, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery, BotCommand
from datetime import datetime
import uuid

from src.config import settings
from src.database.models import User, Product, Category, Order, DailySpin
from src.database import SessionLocal

logger = logging.getLogger(__name__)

# Create router
router = Router()

# Commands
@router.message(Command("start"))
async def start_command(message: Message):
    """Handle /start command"""
    user_id = message.from_user.id
    db = SessionLocal()
    
    # Get or create user
    user = db.query(User).filter(User.telegram_id == user_id).first()
    if not user:
        referral_code = f"ref_{uuid.uuid4().hex[:8]}"
        user = User(
            telegram_id=user_id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            referral_code=referral_code
        )
        db.add(user)
        db.commit()
    
    db.close()
    
    # Send welcome message with main menu
    await message.answer(
        "🛍️ <b>Welcome to NanoToolz!</b>\n\n"
        "Your premium digital products store.\n\n"
        "💰 Credits: 100 | 🎁 Referral Bonus: +50 (pending)\n",
        parse_mode="HTML",
        reply_markup=get_main_menu_keyboard()
    )

def get_main_menu_keyboard():
    """Get main menu inline keyboard"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📚 Browse Store", callback_data="browse")],
        [InlineKeyboardButton(text="🛒 Cart (0)", callback_data="cart"), 
         InlineKeyboardButton(text="⭐ Wishlist", callback_data="wishlist")],
        [InlineKeyboardButton(text="👤 Profile", callback_data="profile"),
         InlineKeyboardButton(text="🆘 Support", callback_data="support")],
        [InlineKeyboardButton(text="🎡 Daily Spin", callback_data="daily_spin"),
         InlineKeyboardButton(text="🎁 Referrals", callback_data="referrals")]
    ])
    return keyboard

@router.message(Command("help"))
async def help_command(message: Message):
    """Handle /help command"""
    await message.answer(
        "📖 <b>NanoToolz Help</b>\n\n"
        "Commands:\n"
        "/start - Start the bot\n"
        "/help - Show this message\n"
        "/profile - View your profile\n"
        "/shop - Browse products\n"
        "/support - Create support ticket\n\n"
        "Need help? Use the Support option in main menu.",
        parse_mode="HTML"
    )

@router.callback_query(F.data == "browse")
async def browse_callback(query: CallbackQuery):
    """Browse products by category"""
    db = SessionLocal()
    categories = db.query(Category).filter(Category.featured == True).all()
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{cat.emoji} {cat.name}", callback_data=f"category_{cat.id}")]
        for cat in categories
    ] + [[InlineKeyboardButton(text="🔙 Back", callback_data="main_menu")]])
    
    db.close()
    
    await query.message.edit_text(
        "📚 <b>Browse Categories</b>\n\nSelect a category to view products:",
        parse_mode="HTML",
        reply_markup=keyboard
    )
    await query.answer()

@router.callback_query(F.data.startswith("category_"))
async def category_products(query: CallbackQuery):
    """Show products in category"""
    category_id = int(query.data.split("_")[1])
    db = SessionLocal()
    
    products = db.query(Product).filter(
        Product.category_id == category_id,
        Product.status == "published"
    ).all()
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"📦 {p.name}", callback_data=f"product_{p.id}")]
        for p in products
    ] + [[InlineKeyboardButton(text="🔙 Back", callback_data="browse")]])
    
    db.close()
    
    await query.message.edit_text(
        f"📦 <b>Products</b>\n\nFound {len(products)} products",
        parse_mode="HTML",
        reply_markup=keyboard
    )
    await query.answer()

@router.callback_query(F.data.startswith("product_"))
async def product_detail(query: CallbackQuery):
    """Show product detail"""
    product_id = int(query.data.split("_")[1])
    db = SessionLocal()
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        await query.answer("Product not found", show_alert=True)
        return
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Add to Cart", callback_data=f"add_cart_{product.id}"),
         InlineKeyboardButton(text="❤️ Wishlist", callback_data=f"wishlist_add_{product.id}")],
        [InlineKeyboardButton(text="📋 Reviews", callback_data=f"reviews_{product.id}")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="browse"),
         InlineKeyboardButton(text="🏠 Home", callback_data="main_menu")]
    ])
    
    stock_status = f"✅ In Stock ({product.stock})" if product.stock and product.stock > 0 else "❌ Out of Stock"
    
    await query.message.edit_text(
        f"<b>{product.name}</b>\n\n"
        f"💰 ${product.price_usd} (≈ {product.price_usdt} USDT)\n"
        f"⭐ {product.rating}/5 ({product.review_count} reviews)\n"
        f"🛍️ {product.sales_count} sold\n"
        f"📦 {stock_status}\n\n"
        f"{product.description}",
        parse_mode="HTML",
        reply_markup=keyboard
    )
    db.close()
    await query.answer()

@router.callback_query(F.data.startswith("add_cart_"))
async def add_to_cart(query: CallbackQuery):
    """Add product to cart"""
    product_id = int(query.data.split("_")[2])
    
    # For now, just show confirmation (cart stored in session/state)
    await query.answer("✅ Added to cart!", show_alert=False)

@router.callback_query(F.data == "profile")
async def profile_callback(query: CallbackQuery):
    """Show user profile"""
    user_id = query.from_user.id
    db = SessionLocal()
    user = db.query(User).filter(User.telegram_id == user_id).first()
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚙️ Settings", callback_data="settings")],
        [InlineKeyboardButton(text="📊 Stats", callback_data="stats")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="main_menu")]
    ])
    
    await query.message.edit_text(
        f"👤 <b>Profile</b>\n\n"
        f"Username: @{user.username or 'N/A'}\n"
        f"💰 Credits: {user.credits}\n"
        f"🎁 Referrals: 0\n"
        f"📦 Orders: 0\n\n"
        f"🔗 Referral Code: <code>{user.referral_code}</code>",
        parse_mode="HTML",
        reply_markup=keyboard
    )
    db.close()
    await query.answer()

@router.callback_query(F.data == "settings")
async def settings_callback(query: CallbackQuery):
    """User settings"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌐 Language", callback_data="language")],
        [InlineKeyboardButton(text="💱 Currency", callback_data="currency")],
        [InlineKeyboardButton(text="🔔 Notifications", callback_data="notifications")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="profile")]
    ])
    
    await query.message.edit_text(
        "⚙️ <b>Settings</b>\n\n"
        "Choose an option to customize your experience:",
        parse_mode="HTML",
        reply_markup=keyboard
    )
    await query.answer()

@router.callback_query(F.data == "currency")
async def currency_settings(query: CallbackQuery):
    """Change currency setting"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇸 USD", callback_data="set_currency_USD")],
        [InlineKeyboardButton(text="🇪🇺 EUR", callback_data="set_currency_EUR")],
        [InlineKeyboardButton(text="🇵🇰 PKR", callback_data="set_currency_PKR")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="settings")]
    ])
    
    await query.message.edit_text(
        "💱 <b>Select Currency</b>\n\n"
        "Choose your preferred currency for pricing:",
        parse_mode="HTML",
        reply_markup=keyboard
    )
    await query.answer()

@router.callback_query(F.data.startswith("set_currency_"))
async def set_currency(query: CallbackQuery):
    """Set user currency"""
    currency = query.data.split("_")[2]
    user_id = query.from_user.id
    db = SessionLocal()
    user = db.query(User).filter(User.telegram_id == user_id).first()
    if user:
        user.currency = currency
        db.commit()
    db.close()
    
    await query.answer(f"✅ Currency changed to {currency}")
    await settings_callback(query)

@router.callback_query(F.data == "daily_spin")
async def daily_spin_callback(query: CallbackQuery):
    """Daily spin"""
    user_id = query.from_user.id
    db = SessionLocal()
    
    # Check if user already spun today
    from datetime import date
    today = date.today()
    spin_today = db.query(DailySpin).filter(
        DailySpin.user_id == query.from_user.id,
        DailySpin.spin_date >= datetime(today.year, today.month, today.day)
    ).first()
    
    if spin_today:
        await query.answer("You already spun today! Try again tomorrow.", show_alert=True)
        db.close()
        return
    
    # Generate reward
    import random
    rewards = [
        ("credits", 50),
        ("credits", 100),
        ("credits", 25),
        ("discount", 10)
    ]
    reward_type, reward_value = random.choice(rewards)
    
    # Save spin
    spin = DailySpin(
        user_id=query.from_user.id,
        reward_type=reward_type,
        reward_value=reward_value
    )
    db.add(spin)
    db.commit()
    db.close()
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍️ Shop", callback_data="browse")],
        [InlineKeyboardButton(text="🏠 Home", callback_data="main_menu")]
    ])
    
    if reward_type == "credits":
        await query.message.edit_text(
            f"🎉 <b>Daily Spin Result!</b>\n\n"
            f"🎯 You won {reward_value} credits!\n\n"
            f"Try again tomorrow!",
            parse_mode="HTML",
            reply_markup=keyboard
        )
    else:
        await query.message.edit_text(
            f"🎉 <b>Daily Spin Result!</b>\n\n"
            f"🎯 You won {reward_value}% discount!\n\n"
            f"Try again tomorrow!",
            parse_mode="HTML",
            reply_markup=keyboard
        )
    
    await query.answer()

@router.callback_query(F.data == "referrals")
async def referrals_callback(query: CallbackQuery):
    """Show referral program"""
    user_id = query.from_user.id
    db = SessionLocal()
    user = db.query(User).filter(User.telegram_id == user_id).first()
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Copy Link", callback_data="copy_referral")],
        [InlineKeyboardButton(text="🏆 Leaderboard", callback_data="leaderboard")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="main_menu")]
    ])
    
    await query.message.edit_text(
        f"🎁 <b>Referral Program</b>\n\n"
        f"Earn 10% commission on every referral!\n\n"
        f"Your Link:\n"
        f"<code>https://t.me/YourBotName?start={user.referral_code}</code>\n\n"
        f"👥 Referrals: 0\n"
        f"💰 Earned: $0.00",
        parse_mode="HTML",
        reply_markup=keyboard
    )
    db.close()
    await query.answer()

@router.callback_query(F.data == "support")
async def support_callback(query: CallbackQuery):
    """Support tickets"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📧 General", callback_data="support_general")],
        [InlineKeyboardButton(text="❌ Order Issue", callback_data="support_order")],
        [InlineKeyboardButton(text="🐛 Bug Report", callback_data="support_bug")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="main_menu")]
    ])
    
    await query.message.edit_text(
        "🆘 <b>Support</b>\n\n"
        "Select a category for your support request:",
        parse_mode="HTML",
        reply_markup=keyboard
    )
    await query.answer()

@router.callback_query(F.data == "main_menu")
async def main_menu_callback(query: CallbackQuery):
    """Return to main menu"""
    await query.message.edit_text(
        "🛍️ <b>Welcome to NanoToolz!</b>\n\n"
        "Your premium digital products store.\n\n"
        "💰 Credits: 100 | 🎁 Referral Bonus: +50 (pending)\n",
        parse_mode="HTML",
        reply_markup=get_main_menu_keyboard()
    )
    await query.answer()

@router.message(Command("shop"))
async def shop_command(message: Message):
    """Direct shop command"""
    await browse_callback(message)

# Fallback
@router.message()
async def echo_handler(message: Message):
    """Echo any unhandled message"""
    await message.answer(
        "I didn't understand that. Use /help for available commands or choose from the menu above.",
        reply_markup=get_main_menu_keyboard()
    )
