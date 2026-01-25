# NanoToolz - Telegram Digital Store Bot (JSON Edition)

High-performance, lightweight Telegram store bot with JSON database, auto-delivery, and inline admin panel.

## 🚀 Features

- **⚡ Fast & Lightweight**: Uses efficient JSON storage (no external DB required).
- **🛍️ Complete Store**: Catalog, Cart, Checkout, and Profile management.
- **🤖 High-Level UX**: Typing indicators, smooth navigation, and reaction feedback.
- **🔐 Inline Admin Panel**: Manage products, stock (keys), and settings directly from Telegram.
- **📦 Auto-Delivery**: Automatically delivers keys/credentials upon purchase.
- **💳 Mock Payments**: Logic ready for Crypto/Card integration.

## 🛠️ Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   Edit `.env` file:
   ```env
   BOT_TOKEN=your_bot_token_here
   ADMIN_IDS=123456789,987654321
   ```

3. **Run the Bot**
   ```bash
   python main.py
   ```

## 📂 Data Structure
The bot creates a `data/` directory automatically:
- `users.json`: User profiles & balances
- `products.json`: Product details & prices
- `stock.json`: Delivery keys/content
- `orders.json`: Purchase history

## 👨‍💻 Admin Usage
- Type `/admin` or use the button in the main menu (if authorized).
- Use the inline panel to Add Products, Upload Stock, and Manage Users.