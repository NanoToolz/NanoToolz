# NanoToolz Setup Instructions

## 🎯 Getting Started in 5 Minutes

### Step 1: Install Dependencies
```bash
cd "/home/dev/Telegram Bots/NanoToolz"
pip install -r requirements.txt
```

If you encounter issues, try:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 2: Get Your Bot Token
1. Open Telegram
2. Search for `@BotFather`
3. Send `/newbot`
4. Follow the prompts to create your bot
5. Copy the token: `123456789:ABCdefGHIjklmnoPQRstuvwxyzABCdefgh`

### Step 3: Configure Environment
```bash
cp .env.example .env
nano .env   # or use your favorite editor
```

Update these values:
```env
BOT_TOKEN=123456789:ABCdefGHIjklmnoPQRstuvwxyzABCdefgh
ADMIN_IDS=YOUR_TELEGRAM_USER_ID
PAYMENT_WALLET_ADDRESS=YOUR_TRON_ADDRESS_HERE
```

### Step 4: Get Your Telegram User ID
- Send `/start` to [@userinfobot](https://t.me/userinfobot)
- Copy the "Your user id:" value
- Paste it in `.env` as `ADMIN_IDS`

### Step 5: Run the Bot!
```bash
python main.py
```

You should see:
```
✅ Bot started! Polling for updates...
```

### Step 6: Test in Telegram
1. Search for your bot name in Telegram
2. Send `/start`
3. You should see the main menu with buttons
4. Try `/help` to see commands

## 🎨 Admin Dashboard (Optional)

In a new terminal:
```bash
uvicorn web.admin:app --reload --host 0.0.0.0 --port 8000
```

Then open: **http://localhost:8000**

You'll see:
- 📊 Sales dashboard
- 📦 Product catalog (15 dummy products pre-loaded)
- 💰 Order history
- 👥 User management

## ✅ Verify Everything Works

Test these features:

1. **Browse Products** - Click "📚 Browse Store"
2. **View Product** - Click any category, then a product
3. **Daily Spin** - Click "🎡 Daily Spin" (once per day)
4. **Referral Program** - Click "🎁 Referrals" to see your link
5. **Profile** - Click "👤 Profile" to see credits & stats
6. **Settings** - Change currency/language in settings

## 💰 Setting Up Crypto Payments

### For USDT (Tron) Payments:

1. **Create Tron Wallet:**
   - Go to TronLink.io or use Ledger/Trust Wallet
   - Create a new wallet
   - Copy your address (starts with T...)

2. **Update .env:**
   ```env
   PAYMENT_WALLET_ADDRESS=TRx...your...address...here
   TRON_PROVIDER_URL=https://api.tronstack.cn
   ```

3. **Fund Your Wallet (Optional for testing):**
   - Small amount of TRX for gas fees
   - Users will send USDT to your address

When a user checks out:
- Bot displays your Tron address
- User sends USDT
- Bot auto-detects payment (within 30 seconds)
- Product automatically delivered!

## 📊 Database

### SQLite (Default - No Setup Needed)
- File: `nanotoolz.db`
- Included with Python
- Perfect for MVP/testing

### PostgreSQL (Production - Optional)
```bash
# Install PostgreSQL on your system first

# Update .env
DATABASE_URL=postgresql://user:password@localhost/nanotoolz

# Install driver
pip install psycopg2-binary

# Run bot
python main.py
```

## 🛑 Common Issues & Fixes

### ❌ "ImportError: No module named 'aiogram'"
```bash
pip install -r requirements.txt
```

### ❌ "BOT_TOKEN not found"
Make sure you have `.env` file with:
```
BOT_TOKEN=your_token_here
```

### ❌ "Database error"
```bash
# Delete old database and reseed
rm nanotoolz.db
python main.py
```

### ❌ "Port 8000 already in use" (for admin panel)
```bash
# Use different port
uvicorn web.admin:app --port 8001
```

## 🔐 Production Checklist

Before going live:

- [ ] Change `ADMIN_SECRET_KEY` in `.env`
- [ ] Use PostgreSQL instead of SQLite
- [ ] Set `DEBUG=False` in `.env`
- [ ] Deploy on VPS/Cloud (not local machine)
- [ ] Set up HTTPS for admin panel
- [ ] Regular database backups
- [ ] Monitor error logs

## 📦 What's Included

✅ **Pre-loaded Dummy Data:**
- 5 product categories
- 15 sample digital products
  - Courses (Python, Telegram Bot Dev, Web Dev)
  - License Keys (Windows, Office, Adobe)
  - Tools (Video Editor, SEO Tool, Photo Editor)
  - Templates (UI Kits, Icons, Website Templates)
  - E-Books (Marketing, Crypto, Freelancing)
- All ready to sell!

✅ **Bot Features Ready:**
- Shopping cart
- Product browsing
- Checkout flow
- Referral system
- Daily spin rewards
- Support tickets
- Multi-currency support
- Multi-language UI

✅ **Admin Dashboard:**
- Product management
- Order tracking
- Sales analytics
- User management
- Broadcasting

## 🚀 Next Steps

1. **Customize Products:**
   - Go to http://localhost:8000
   - Edit products, prices, descriptions
   - Upload your own product images

2. **Add More Categories:**
   ```bash
   # In admin dashboard, click "📂 Categories"
   ```

3. **Configure Payments:**
   - Add your Tron wallet address
   - Test a payment flow

4. **Deploy:**
   - Use Railway.app, DigitalOcean, or VPS
   - Keep bot running 24/7

## 📞 Need Help?

- **Bot Help:** Send `/help` to the bot
- **Setup Issues:** Check your `.env` file
- **Payment Questions:** See PAYMENT_WALLET_ADDRESS setup above
- **Admin Dashboard:** http://localhost:8000

---

**You're all set! 🎉**

Your NanoToolz bot is ready to accept orders and payments!

Send `/start` to your bot to begin.
