# NanoToolz Bot - Complete Deployment Guide

## 🎯 What You've Got

A **production-ready Telegram store bot** with:
- ✅ 15 dummy digital products pre-loaded
- ✅ 5 product categories
- ✅ Complete shopping flow
- ✅ Referral system with credits
- ✅ Daily spin gamification
- ✅ Support ticket system
- ✅ Admin web dashboard
- ✅ Multi-currency & language support

## 🚀 Getting Started (5 Minutes)

### Step 1: Update Configuration
```bash
cd "/home/dev/Telegram Bots/NanoToolz"

# Edit .env file
nano .env
```

Update these lines:
```env
BOT_TOKEN=PASTE_YOUR_BOT_TOKEN_HERE
ADMIN_IDS=YOUR_TELEGRAM_USER_ID
PAYMENT_WALLET_ADDRESS=YOUR_TRON_ADDRESS_HERE
```

**How to get these values:**
- **BOT_TOKEN**: Message @BotFather on Telegram, use `/newbot`
- **ADMIN_IDS**: Message @userinfobot on Telegram, copy your user ID
- **PAYMENT_WALLET_ADDRESS**: Create wallet on TronLink.io (starts with T...)

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run the Bot
```bash
python main.py
```

Expected output:
```
🗄️  Initializing database...
🌱 Seeding dummy data...
🤖 Starting bot...
✅ Bot started! Polling for updates...
```

### Step 4: Test in Telegram
1. Find your bot (search bot username)
2. Send `/start`
3. Click buttons to test!

## 💻 Running Both Bot & Admin Panel

**Terminal 1 - Bot:**
```bash
python main.py
```

**Terminal 2 - Admin Dashboard:**
```bash
uvicorn web.admin:app --reload --host 0.0.0.0 --port 8000
```

Then open: **http://localhost:8000**
- Username: `admin`
- Password: `password123`

## 📦 Project Structure

```
NanoToolz/
├── main.py                    # Bot entry point ⭐ RUN THIS
├── requirements.txt           # Python dependencies
├── .env                       # Configuration (YOUR TOKEN HERE)
├── .env.example              # Template
├── README.md                 # Full documentation
├── SETUP.md                  # Setup instructions
├── QUICKSTART.py             # Quick start guide
│
├── src/
│   ├── config.py             # Settings loader
│   ├── messages.py           # Bot messages & i18n
│   ├── utils.py              # Helper functions
│   ├── cache.py              # In-memory state
│   ├── seed.py               # Dummy data generator
│   │
│   ├── bot/
│   │   ├── __init__.py       # Bot initialization
│   │   └── handlers.py       # Message & callback handlers
│   │
│   └── database/
│       ├── __init__.py       # DB connection
│       └── models.py         # SQLAlchemy ORM models
│
├── web/
│   ├── admin.py              # FastAPI admin dashboard ⭐ OPTIONAL
│   └── static/               # CSS/JS assets
│
└── nanotoolz.db              # SQLite database (auto-created)
```

## 🎯 Features You Can Test Now

### Bot Features
1. **/start** - Main menu with buttons
2. **📚 Browse Store** - View categories & products
3. **📦 Product Details** - Price, rating, reviews
4. **🛒 Add to Cart** - Shopping cart system
5. **💰 Checkout** - Shows wallet address for USDT payment
6. **👤 Profile** - View credits, orders, referral link
7. **🎡 Daily Spin** - Win rewards (once per day)
8. **🎁 Referrals** - Earn 10% commission
9. **🆘 Support** - Create & track tickets
10. **⚙️ Settings** - Change currency & language

### Admin Dashboard Features
- 📊 Sales dashboard with metrics
- 📦 Product management (add, edit, delete)
- 👥 User management
- 💰 Order tracking
- 📊 Analytics & graphs
- 📢 Broadcast messages
- 🎫 Support ticket management

## 💰 How Payments Work

### Current Setup (USDT on Tron)
```
User adds products → Checkout → Bot shows address & QR code
→ User sends USDT → Bot detects payment (30 sec)
→ Product auto-delivered
```

**To receive payments:**
1. Set your Tron wallet address in `.env`
2. Bot will monitor this address for incoming USDT
3. Auto-confirm orders when payment detected

### Test Without Real Payments
- Leave `PAYMENT_WALLET_ADDRESS` as placeholder
- Checkout flow still works (just won't auto-verify)
- For testing, use credits instead

## 🗄️ Database

### Default: SQLite (Built-in, No Setup)
- File: `nanotoolz.db`
- Auto-created on first run
- Great for MVP/testing

### Production: PostgreSQL (Recommended)
1. Install PostgreSQL
2. Update `.env`:
   ```env
   DATABASE_URL=postgresql://user:password@localhost/nanotoolz
   ```
3. Install driver:
   ```bash
   pip install psycopg2-binary
   ```

## 📊 Dummy Data Included

The database comes pre-seeded with:

### Products (15 total)
- **Courses**: Python 101, Telegram Bot Dev, Web Dev Bootcamp
- **Licenses**: Windows 10, Office 2024, Adobe Creative Cloud
- **Tools**: Video Editor, SEO Tool, Photo Editor
- **Templates**: Figma UI Kits, Icon Pack, Website Templates
- **E-Books**: Digital Marketing, Crypto Guide, Freelancing

### All Features Pre-Configured
- ✅ Prices in USD & USDT
- ✅ Stock quantities
- ✅ Ratings & reviews (dummy data)
- ✅ Affiliate commissions
- ✅ Ready to deliver (dummy files/keys)

## 🚀 Deployment Options

### Option 1: VPS (Best for Control)
```bash
# SSH into server
ssh user@your-vps.com

# Clone repo & setup
git clone <your-repo>
cd NanoToolz
pip install -r requirements.txt

# Run in background
nohup python main.py > bot.log 2>&1 &

# View logs
tail -f bot.log
```

### Option 2: Railway.app (Easy & Free)
1. Push to GitHub
2. Go to railway.app
3. Connect GitHub repo
4. Add environment variables (.env)
5. Deploy!

### Option 3: Docker
```dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

Build & run:
```bash
docker build -t nanotoolz .
docker run -e BOT_TOKEN=YOUR_TOKEN nanotoolz
```

## 🔐 Security Checklist

- [ ] Change `ADMIN_SECRET_KEY` in `.env` to random string
- [ ] Keep `.env` private (in .gitignore)
- [ ] Don't commit `.env` file to Git
- [ ] Use strong admin password
- [ ] Set `DEBUG=False` for production
- [ ] Use PostgreSQL instead of SQLite for production
- [ ] Enable HTTPS for admin dashboard
- [ ] Set up regular database backups

## 📝 Customization

### Change Product Data
```bash
# Edit in admin dashboard
http://localhost:8000
```

### Add New Category
```python
from src.database.models import Category
from src.database import SessionLocal

db = SessionLocal()
cat = Category(name="My Category", emoji="🎯")
db.add(cat)
db.commit()
```

### Add New Product
```python
from src.database.models import Product
from src.database import SessionLocal

db = SessionLocal()
prod = Product(
    category_id=1,
    name="My Product",
    price_usd=49.99,
    price_usdt=49.50,
    description="..."
)
db.add(prod)
db.commit()
```

### Reset Dummy Data
```bash
rm nanotoolz.db
python main.py  # Will reseed
```

## ⚙️ Configuration Options

All settings in `.env`:

```env
# Bot
BOT_TOKEN=your_token_here
ADMIN_IDS=123456789,987654321  # Multiple admins supported

# Database
DATABASE_URL=sqlite:///nanotoolz.db
# Or: postgresql://user:pass@host/db

# Payments
TRON_PROVIDER_URL=https://api.tronstack.cn
PAYMENT_WALLET_ADDRESS=TRx...

# Currency
PRIMARY_CURRENCY=USD  # USD, EUR, PKR, INR, etc.
EXCHANGE_RATE_API=coingecko

# App
APP_ENV=development  # or production
DEBUG=True  # False for production

# Admin
ADMIN_USERNAME=admin
ADMIN_PASSWORD=password123  # CHANGE THIS!
```

## 🐛 Troubleshooting

### Bot Won't Start
```
❌ "ModuleNotFoundError: No module named 'aiogram'"
✅ Solution: pip install -r requirements.txt
```

### Token Error
```
❌ "Invalid bot token"
✅ Solution: Check BOT_TOKEN in .env (from @BotFather)
```

### Admin Dashboard Won't Load
```
❌ "Connection refused on port 8000"
✅ Solution: uvicorn web.admin:app --port 8001
```

### Database Error
```
❌ "database is locked" or "no table"
✅ Solution: rm nanotoolz.db && python main.py
```

## 📞 Next Steps

1. **Customize products** in admin dashboard
2. **Test payment flow** with test wallet
3. **Configure referral rates** (currently 10%)
4. **Set daily spin rewards**
5. **Add your branding** (colors, messages)
6. **Deploy to production** (Railway, VPS, Docker)
7. **Go live!** 🎉

## 📚 Additional Resources

- **Aiogram Docs**: https://docs.aiogram.dev/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org/
- **Telegram Bot API**: https://core.telegram.org/bots/api
- **Tron Docs**: https://developers.tron.network/

## 🎉 You're All Set!

Your NanoToolz bot is **production-ready** with:
- ✅ Complete shopping experience
- ✅ 15 sample products
- ✅ Crypto payment integration
- ✅ Referral system
- ✅ Gamification
- ✅ Admin dashboard
- ✅ All configurations pre-setup

### To Start:
```bash
python main.py
```

### Find Your Bot:
Search for it on Telegram by username

### Send Commands:
- `/start` - Main menu
- `/help` - Commands
- `/shop` - Browse

That's it! Your store is live! 🚀

---

**Questions?** Check SETUP.md or README.md for more details.

**Issues?** Review .env configuration and ensure BOT_TOKEN is correct.

**Ready to deploy?** See the Deployment Options section above.

Happy selling! 💰
