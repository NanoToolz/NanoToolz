# 🤖 NanoToolz - Telegram Store Bot

**High-performance, lightweight Telegram store bot with JSON database, auto-delivery, and inline admin panel.**

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
src/bot/features/
├── start.py          # /start command & main menu
├── catalog.py        # Browse products & categories
├── cart.py           # Shopping cart management
├── checkout.py       # Payment processing & orders
├── profile.py        # User profile & order history
├── topup.py          # Balance topup
├── admin.py          # Admin panel & product management
├── help.py           # Help & FAQ
├── support.py        # Support center
├── referral.py       # Referral program
├── rewards.py        # Daily spin & rewards
└── wishlist.py       # Wishlist management
```

---

## 📝 Code Structure

Each feature file has this structure:

```python
# ============================================
# FEATURE: [Name]
# ============================================

# ===== IMPORTS =====
# All imports here

# ===== MESSAGES SECTION =====
# All text messages here
# Detailed comments explain each message

# ===== KEYBOARDS SECTION =====
# All button layouts here
# Detailed comments explain each keyboard

# ===== HANDLERS SECTION =====
# All command handlers here
# Detailed comments explain each handler
```

---

## 🎯 How to Update Features

### Update Welcome Message
1. Open `src/bot/features/start.py`
2. Find `# ===== MESSAGES SECTION =====`
3. Edit `get_welcome_text()` function
4. Save & restart bot: `python main.py`

### Add New Button
1. Open feature file (e.g., `start.py`)
2. Find `# ===== KEYBOARDS SECTION =====`
3. Add button to keyboard function
4. Save & restart bot

### Change Product Display
1. Open `src/bot/features/catalog.py`
2. Find `PRODUCT_DETAIL_TEMPLATE`
3. Edit template
4. Save & restart bot

### Add New Payment Method
1. Open `src/bot/features/checkout.py`
2. Find `def get_checkout_keyboard()`
3. Add button for new payment method
4. Add handler for payment processing
5. Save & restart bot

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

### Start (`start.py`)
- Handles `/start` command
- Registers new users
- Shows main menu with all options
- Displays welcome image if available

### Catalog (`catalog.py`)
- Browse product categories
- View products in category
- Show product details with image
- Check stock availability

### Cart (`cart.py`)
- Add products to cart
- Increase/decrease quantity
- Remove items
- View cart with total price

### Checkout (`checkout.py`)
- Show order summary
- Select payment method
- Process payment (credits or external)
- Auto-deliver keys/credentials
- Create order record

### Profile (`profile.py`)
- Display user stats (ID, name, balance, orders)
- Show order history (last 5 orders)
- Quick access to topup and shopping

### Topup (`topup.py`)
- Select topup amount ($10-$500)
- Choose payment method (Crypto/Card mock)
- Update user balance
- Show success confirmation

### Admin (`admin.py`)
- Add new products
- Set product prices
- Upload stock keys
- Manage product inventory
- Admin-only access

### Help (`help.py`)
- How to shop guide
- Payment methods info
- Delivery information
- FAQ topics

### Support (`support.py`)
- General support
- Billing support
- Technical support
- Contact information

### Referral (`referral.py`)
- Show referral code
- Track referrals
- Copy referral link
- Earn commissions

### Rewards (`rewards.py`)
- Daily spin wheel
- Win credits or discounts
- One spin per day limit
- Random reward selection

### Wishlist (`wishlist.py`)
- Add products to wishlist
- Remove from wishlist
- View saved products
- Quick access to favorites

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
- Or click "Admin Panel" button in main menu (if authorized)

### Add Product
1. Click "Manage Products"
2. Click "Add Product"
3. Enter product name
4. Enter product price
5. Click "Add Stock" to upload keys

### Upload Stock
1. Click "Add Stock" for a product
2. Send keys (one per line)
3. Keys are saved and ready for delivery

---

## 🎯 Callback Data Reference

| Feature | Callback | Purpose |
|---------|----------|---------|
| Start | `catalog_main` | Browse catalog |
| Start | `cart_view` | View cart |
| Start | `topup` | Topup balance |
| Start | `profile_view` | View profile |
| Start | `admin` | Admin panel |
| Catalog | `cat_*` | Show category products |
| Catalog | `prod_*` | Show product details |
| Cart | `add_cart_*` | Add to cart |
| Cart | `cart_inc_*` | Increase quantity |
| Cart | `cart_dec_*` | Decrease quantity |
| Cart | `cart_rem_*` | Remove item |
| Checkout | `checkout_start` | Start checkout |
| Checkout | `pay_credits` | Pay with credits |
| Checkout | `pay_external` | Pay with card/crypto |
| Profile | `order_history` | View order history |
| Admin | `admin_products` | Manage products |
| Admin | `add_product` | Add new product |
| Admin | `edit_prod_*` | Edit product |
| Admin | `add_stock_*` | Add stock keys |

---

## 🚨 Troubleshooting

### Bot not responding
1. Check if bot token is correct in `.env`
2. Verify internet connection
3. Restart bot: `python main.py`

### Changes not taking effect
1. Save file (Ctrl+S)
2. Restart bot (Ctrl+C, then `python main.py`)
3. Clear Telegram cache (optional)

### Import errors
1. Check file path in import statement
2. Verify `router` is defined in feature file
3. Check for typos in callback_data

### Buttons not appearing
1. Verify keyboard function is called in handler
2. Check `reply_markup=` parameter is set
3. Verify button callback_data matches handler

---

## 📚 Code Comments

Every file has detailed comments explaining:
- What each section does
- What each function does
- What each variable means
- How to use and modify the code

**Example:**
```python
# Extract product ID from callback_data
# Format: "prod_42" -> extract "42"
prod_id = int(callback.data.split("_")[1])
```

---

## 🎓 Learning Path

1. **Understand Structure** - Read this README
2. **Explore Code** - Open `src/bot/features/start.py`
3. **Make First Update** - Change welcome message
4. **Test Changes** - Run bot and verify
5. **Create Feature** - Follow template to add new feature
6. **Master Bot** - Explore all features and customize

---

## 💡 Pro Tips

- Use Ctrl+F to search for callback_data
- Keep messages and keyboards together
- Test after each change
- Always restart bot after editing
- Use this structure for all new features
- Add detailed comments to your code

---

## 📞 Quick Reference

| Task | File | Section |
|------|------|---------|
| Update welcome | `start.py` | `# ===== MESSAGES SECTION =====` |
| Add button | `[feature].py` | `# ===== KEYBOARDS SECTION =====` |
| Change message | `[feature].py` | `# ===== MESSAGES SECTION =====` |
| Add handler | `[feature].py` | `# ===== HANDLERS SECTION =====` |
| Create feature | `features/newfeature.py` | Use template |
| Register feature | `routers.py` | Add import & include_router |

---

## ✅ Features Checklist

- ✅ Start command & main menu
- ✅ Product catalog with categories
- ✅ Shopping cart with quantity controls
- ✅ Checkout with payment methods
- ✅ User profile & order history
- ✅ Balance topup
- ✅ Admin panel for product management
- ✅ Help & FAQ
- ✅ Support center
- ✅ Referral program
- ✅ Daily rewards spin
- ✅ Wishlist management

---

## 🎉 Summary

Your bot is:
- ✅ **Clean** - One file per feature
- ✅ **Organized** - Clear sections with separators
- ✅ **Documented** - Detailed comments throughout
- ✅ **Maintainable** - Easy to update & extend
- ✅ **Production-Ready** - Tested & verified
- ✅ **Scalable** - Ready for new features

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

*For detailed code examples and explanations, check the comments in each feature file.*
