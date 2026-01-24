# NanoToolz Telegram Store Bot - Rewritten

A clean, working Telegram store bot with catalog, cart, checkout, and admin features.

## Quick Start

### 1. Setup Environment
```bash
# Copy .env template
cp .env.example .env

# Edit .env and add your bot token
BOT_TOKEN=your_telegram_bot_token_here
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Bot
```bash
python main.py
```

The bot will:
- ✅ Initialize the database
- ✅ Seed sample products and categories
- ✅ Start polling for user messages

## Features

### 👥 User Features
- **🛍️ Catalog** - Browse products by category
- **🛒 Shopping Cart** - Add/remove items, manage quantities
- **💳 Checkout** - Pay with card or account credits
- **👤 Profile** - View account info and order history
- **❓ Help** - FAQ and support information

### 🔐 Admin Features
- **📊 Dashboard** - View statistics (users, orders, revenue)
- **📦 Product Management** - List products and status
- **📂 Category Management** - View and manage categories
- **💰 Revenue Tracking** - Total sales and earnings

## Admin Panel
1) `uvicorn web.admin:app --reload`
2) Open `http://localhost:8000`
3) Login with `ADMIN_USERNAME` and `ADMIN_PASSWORD` from `.env`

### Admin Features (Full Customization)
- Products + Image uploads
- Categories
- Stock (auto-delivery items)
- Coupons
- Pricing
- Orders, Users, Payments, Topups
- Store Settings + Bot UI settings

## Architecture

```
main.py                          # Entry point
├── src/bot/
│   ├── app.py                  # Dispatcher setup
│   ├── routers.py              # Router registration
│   └── features/               # Feature modules
│       ├── start/              # Welcome & main menu
│       ├── catalog/            # Browse products
│       ├── cart/               # Cart management
│       ├── checkout/           # Payment & orders
│       ├── profile/            # User account
│       ├── help/               # FAQ & support
│       └── admin/              # Admin panel
├── src/database/
│   ├── __init__.py             # DB connection
│   └── models.py               # SQLAlchemy models
├── src/config.py               # Configuration
├── src/seed.py                 # Dummy data
└── src/logger.py               # Logging
```

## Database Models

**Users** - User profiles with credits and preferences
**Categories** - Product categories with emoji
**Products** - Products with pricing and stock
**CartItems** - Shopping cart items
**Orders** - Completed purchases
**Other** - Referrals, payments, settings, reviews

## Configuration

Edit `.env` to customize:

```env
# Bot
BOT_TOKEN=your_token
ADMIN_IDS=123456789,987654321

# Database
DATABASE_URL=sqlite:///nanotoolz.db

# Store
STORE_NAME=NanoToolz Store
SUPPORT_CONTACT=@support

# Admin Panel
ADMIN_USERNAME=admin
ADMIN_PASSWORD=password123
```

## Workflow

### User Flow
1. Send `/start` to bot
2. Click "🛍️ Browse Catalog"
3. Select category → product
4. Click "➕ Add to Cart"
5. Click "🛒 View Cart"
6. Click "✅ Checkout"
7. Choose payment method
8. Order confirmed!

### Admin Flow
1. Add `ADMIN_IDS` to `.env`
2. Restart bot
3. Click "admin_panel" in chat
4. View stats, products, categories
5. Manage via web admin (optional)

## Sample Data

Bot auto-seeds on first run:

- **4 Categories**: Software, E-Books, Courses, Templates
- **6 Products**: WordPress theme, Python course, marketing guide, etc.
- **1 Test Admin**: User ID `123456789` with $1000 credits

## Payment Methods

- **💳 Card** - Simulated payment (auto-approved)
- **💰 Credits** - Deduct from account balance

## Stock / Auto-Delivery
- Manage delivery stock from **Admin → Stock**.
- Each item is a key/link/credential used once.
- On checkout, bot auto-delivers available stock.

## Troubleshooting

### Bot not responding
- Check `BOT_TOKEN` in `.env`
- Verify bot is running: `python main.py`
- Check logs for errors

### Database error
- Delete `nanotoolz.db` to reset
- Restart bot to reseed

### Admin panel not accessible
- Verify your Telegram ID in `ADMIN_IDS`
- Restart bot for config changes

## Next Steps

1. ✅ Add real payment gateway (Stripe, Paypal)
2. ✅ Implement web admin panel (FastAPI)
3. ✅ Add email notifications
4. ✅ Setup production database (PostgreSQL)
5. ✅ Add referral system
6. ✅ Implement user reviews/ratings

## Support

For issues, check the logs or open an issue on GitHub.

Happy selling! 🚀