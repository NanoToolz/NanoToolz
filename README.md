# 🤖 NanoToolz - Telegram Store Bot

**Simple, lightweight Telegram store bot with JSON database and auto-delivery.**

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Edit `.env` file:
```env
BOT_TOKEN=your_bot_token_here
ADMIN_IDS=123456789,987654321
```

### 3. Run the Bot
```bash
python main.py
```

---

## 📁 Project Structure

```
NanoToolz/
├── src/
│   ├── bot/
│   │   ├── features/          # All bot features (12 files)
│   │   │   ├── start.py       # /start command
│   │   │   ├── catalog.py     # Browse products
│   │   │   ├── cart.py        # Shopping cart
│   │   │   ├── checkout.py    # Payment & orders
│   │   │   ├── profile.py     # User profile
│   │   │   ├── topup.py       # Balance topup
│   │   │   ├── admin.py       # Admin panel
│   │   │   ├── help.py        # Help & FAQ
│   │   │   ├── support.py     # Support
│   │   │   ├── referral.py    # Referral
│   │   │   ├── rewards.py     # Daily spin
│   │   │   └── wishlist.py    # Wishlist
│   │   ├── app.py             # Bot initialization
│   │   └── routers.py         # Router registration
│   ├── database/
│   │   └── json_db.py         # JSON database
│   ├── config.py              # Settings
│   └── logger.py              # Logging
├── data/                       # JSON database files
├── main.py                     # Entry point
├── README.md                   # This file
└── requirements.txt            # Dependencies
```

---

## 📝 Code Structure

Each feature file has this structure:

```python
# ============================================
# FEATURE: [Name]
# ============================================

# ===== IMPORTS =====
# All imports

# ===== MESSAGES SECTION =====
# All text messages with detailed comments

# ===== KEYBOARDS SECTION =====
# All button layouts with detailed comments

# ===== HANDLERS SECTION =====
# All command handlers with detailed comments
```

---

## 🎯 How to Update Features

### Update Welcome Message
1. Open `src/bot/features/start.py`
2. Find `# ===== MESSAGES SECTION =====`
3. Edit `get_welcome_text()` function
4. Save & restart: `python main.py`

### Add New Button
1. Open feature file (e.g., `start.py`)
2. Find `# ===== KEYBOARDS SECTION =====`
3. Add button to keyboard function
4. Save & restart

### Change Product Display
1. Open `src/bot/features/catalog.py`
2. Find `PRODUCT_DETAIL_TEMPLATE`
3. Edit template
4. Save & restart

---

## 🔧 Creating New Features

### Step 1: Create Feature File
```bash
touch src/bot/features/myfeature.py
```

### Step 2: Use Template
```python
# ============================================
# FEATURE: My Feature
# ============================================

# ===== IMPORTS =====
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

# ===== MESSAGES SECTION =====
MY_MESSAGE = "Hello from my feature!"

# ===== KEYBOARDS SECTION =====
def get_my_keyboard() -> InlineKeyboardMarkup:
    """Build my feature keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Back", callback_data="back_main")]
    ])

# ===== HANDLERS SECTION =====
@router.callback_query(F.data == "myfeature")
async def my_handler(callback: CallbackQuery):
    """Handle my feature"""
    await callback.message.edit_text(MY_MESSAGE, reply_markup=get_my_keyboard())
    await callback.answer()
```

### Step 3: Register in routers.py
```python
from src.bot.features.myfeature import router as myfeature_router

def setup_routers(dp: Dispatcher) -> None:
    dp.include_router(myfeature_router)
    # ... other routers
```

### Step 4: Add Button to Main Menu
Edit `src/bot/features/start.py`:
```python
def get_main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            # ... existing buttons
            [InlineKeyboardButton(text="✨ My Feature", callback_data="myfeature")],
        ]
    )
```

---

## 📊 Features Overview

| Feature | File | Purpose |
|---------|------|---------|
| Start | `start.py` | /start command & main menu |
| Catalog | `catalog.py` | Browse products & categories |
| Cart | `cart.py` | Shopping cart management |
| Checkout | `checkout.py` | Payment & order delivery |
| Profile | `profile.py` | User profile & order history |
| Topup | `topup.py` | Balance topup |
| Admin | `admin.py` | Admin panel & customization |
| Help | `help.py` | Help & FAQ |
| Support | `support.py` | Support center |
| Referral | `referral.py` | Referral program |
| Rewards | `rewards.py` | Daily spin & rewards |
| Wishlist | `wishlist.py` | Wishlist management |

---

## 💾 Database Structure

```
data/
├── users.json       # User profiles & balances
├── products.json    # Product details & prices
├── stock.json       # Delivery keys/content
├── orders.json      # Purchase history
├── categories.json  # Product categories
├── coupons.json     # Discount coupons
└── settings.json    # Bot settings
```

---

## 🔐 Admin Usage

### Access Admin Panel
- Type `/admin` command
- Or click "Admin Panel" button in main menu

### Customize Welcome
1. Click "Customize Welcome"
2. Click "Change Welcome Text" to set custom message
3. Click "Change Welcome Image" to upload picture

### Add Product
1. Click "Manage Products"
2. Click "Add Product"
3. Enter product name and price
4. Click "Add Stock" to upload keys

---

## 🎯 Callback Data Reference

| Feature | Callback | Purpose |
|---------|----------|---------|
| Start | `catalog_main` | Browse catalog |
| Start | `cart_view` | View cart |
| Start | `topup` | Topup balance |
| Start | `profile_view` | View profile |
| Catalog | `cat_*` | Show category products |
| Catalog | `prod_*` | Show product details |
| Cart | `add_cart_*` | Add to cart |
| Cart | `cart_inc_*` | Increase quantity |
| Cart | `cart_dec_*` | Decrease quantity |
| Cart | `cart_rem_*` | Remove item |
| Checkout | `checkout_start` | Start checkout |
| Checkout | `pay_credits` | Pay with credits |
| Checkout | `pay_external` | Pay with card/crypto |

---

## 🚨 Troubleshooting

### Bot not responding
1. Check bot token in `.env`
2. Verify internet connection
3. Restart bot: `python main.py`

### Changes not taking effect
1. Save file (Ctrl+S)
2. Restart bot (Ctrl+C, then `python main.py`)

### Import errors
1. Check file path in import
2. Verify `router` is defined
3. Check for typos in callback_data

---

## 💡 Pro Tips

- Use Ctrl+F to search for callback_data
- Keep messages and keyboards together
- Test after each change
- Always restart bot after editing
- Add detailed comments to your code

---

## ✅ Features Checklist

- ✅ Start command & main menu
- ✅ Product catalog with categories
- ✅ Shopping cart with quantity controls
- ✅ Checkout with payment methods
- ✅ User profile & order history
- ✅ Balance topup
- ✅ Admin panel with customization
- ✅ Help & FAQ
- ✅ Support center
- ✅ Referral program
- ✅ Daily rewards spin
- ✅ Wishlist management

---

## 🎉 Summary

Your bot is:
- ✅ **Simple** - Clean, easy to understand
- ✅ **Organized** - One file per feature
- ✅ **Documented** - Detailed comments throughout
- ✅ **Maintainable** - Easy to update & extend
- ✅ **Production-Ready** - Tested & verified

---

## 🚀 Get Started

1. **Install:** `pip install -r requirements.txt`
2. **Configure:** Edit `.env` file
3. **Run:** `python main.py`
4. **Test:** Send `/start` command
5. **Update:** Follow guides above
6. **Extend:** Create new features

---

**Happy coding! 🎉**
