#!/usr/bin/env python3
"""
NanoToolz Bot - Quick Start Guide
Run this script to understand what to do next
"""

def print_guide():
    guide = """
╔════════════════════════════════════════════════════════════════════╗
║            🛍️ NanoToolz - Telegram Store Bot                      ║
║                    QUICK START GUIDE                              ║
╚════════════════════════════════════════════════════════════════════╝

📋 CHECKLIST - Complete these steps:

1️⃣ GET YOUR BOT TOKEN
   ─────────────────────────────────────────────────────────────
   • Open Telegram → Search "@BotFather"
   • Send: /newbot
   • Follow prompts, give it a name & username
   • Copy the token (looks like: 123456:ABC...)
   • Paste it in .env file: BOT_TOKEN=YOUR_TOKEN_HERE

2️⃣ GET YOUR TELEGRAM USER ID
   ─────────────────────────────────────────────────────────────
   • Search "@userinfobot" on Telegram
   • Click /start
   • Copy "Your user id: 123456789"
   • Paste in .env file: ADMIN_IDS=YOUR_ID

3️⃣ GET TRON WALLET ADDRESS (OPTIONAL - For payments)
   ─────────────────────────────────────────────────────────────
   • Install TronLink wallet or use Ledger/Trust Wallet
   • Create new wallet
   • Copy address (starts with T...)
   • Paste in .env: PAYMENT_WALLET_ADDRESS=T...

4️⃣ INSTALL & RUN
   ─────────────────────────────────────────────────────────────
   $ pip install -r requirements.txt
   $ python main.py

5️⃣ TEST IN TELEGRAM
   ─────────────────────────────────────────────────────────────
   • Find your bot on Telegram
   • Send /start
   • Click buttons to test features

6️⃣ (OPTIONAL) RUN ADMIN DASHBOARD
   ─────────────────────────────────────────────────────────────
   • Open another terminal
   $ uvicorn web.admin:app --reload
   • Go to: http://localhost:8000
   • Username: admin | Password: password123

═════════════════════════════════════════════════════════════════════

📦 WHAT'S INCLUDED:

✅ Complete Bot (ready to use)
   ├─ 15 dummy products (courses, licenses, tools, templates, ebooks)
   ├─ 5 product categories
   ├─ Shopping cart & checkout
   ├─ Referral system
   ├─ Daily spin rewards
   ├─ Support tickets
   ├─ Multi-currency & language support
   └─ User profiles

✅ Admin Dashboard
   ├─ Product management
   ├─ Order tracking
   ├─ User analytics
   ├─ Sales metrics
   └─ Broadcasting

✅ Database (SQLite)
   └─ Pre-seeded with dummy data

═════════════════════════════════════════════════════════════════════

🎯 BOT FEATURES TO TEST:

1. /start              → Main menu
2. 📚 Browse Store     → See all products
3. 💰 Add to Cart      → Select product
4. 🛒 Cart             → View & checkout
5. 👤 Profile          → Your account
6. 🎡 Daily Spin       → Win rewards (once/day)
7. 🎁 Referrals        → Share & earn
8. 🆘 Support          → Create tickets
9. ⚙️ Settings         → Language/Currency

═════════════════════════════════════════════════════════════════════

💰 PAYMENT FLOW:

User adds products → Clicks "Checkout" → Bot shows USDT address 
→ User sends USDT → Bot auto-detects (30 sec) → Product delivered!

(You need PAYMENT_WALLET_ADDRESS set in .env for this)

═════════════════════════════════════════════════════════════════════

📊 ADMIN DASHBOARD:

URL: http://localhost:8000
Username: admin
Password: password123

Features:
• Dashboard with sales metrics
• Product management
• Category management
• Order history
• User management
• Broadcast messages
• Settings

═════════════════════════════════════════════════════════════════════

🔧 FILES TO KNOW:

.env                  → Configuration (passwords, tokens, wallet)
main.py               → Bot entry point
src/bot/handlers.py   → Bot commands & handlers
src/database/models.py → Database schema
src/seed.py           → Dummy data (15 products)
web/admin.py          → Admin dashboard

═════════════════════════════════════════════════════════════════════

⚠️ IMPORTANT NOTES:

• .env is in .gitignore (private, never push)
• Default database: SQLite (no setup needed)
• For production: Use PostgreSQL
• Keep BOT_TOKEN secret!
• Admin panel password: change "password123" in .env

═════════════════════════════════════════════════════════════════════

🚀 NEXT STEPS AFTER SETUP:

1. Customize products in admin dashboard
2. Change prices, descriptions, images
3. Add more categories
4. Configure payment wallet
5. Test payment flow
6. Deploy to VPS/Cloud (Railway.app, DigitalOcean, etc.)

═════════════════════════════════════════════════════════════════════

❓ TROUBLESHOOTING:

"ModuleNotFoundError" 
  → pip install -r requirements.txt

"BOT_TOKEN not found"
  → Check .env file exists and has BOT_TOKEN=...

"Port 8000 in use" (admin panel)
  → uvicorn web.admin:app --port 8001

Database error
  → rm nanotoolz.db && python main.py

═════════════════════════════════════════════════════════════════════

📧 SUPPORT:

Check bot /help command in Telegram
Or create support ticket in bot menu

═════════════════════════════════════════════════════════════════════

Ready? Let's go! 🎉

1. Add BOT_TOKEN to .env
2. Run: python main.py
3. Find your bot on Telegram
4. Send /start
5. Start selling! 🚀

═════════════════════════════════════════════════════════════════════
    """
    print(guide)

if __name__ == "__main__":
    print_guide()
    
    import os
    print("\n" + "="*70)
    print("📝 CHECKING YOUR SETUP...\n")
    
    # Check .env
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            env_content = f.read()
            
        if "PASTE_YOUR_BOT_TOKEN_HERE" in env_content:
            print("⚠️  BOT_TOKEN not set - Add your token to .env")
        elif "YOUR_BOT_TOKEN_HERE" in env_content:
            print("⚠️  BOT_TOKEN needs configuration")
        else:
            print("✅ BOT_TOKEN appears to be configured")
        
        if "123456789" in env_content and "ADMIN_IDS=123456789" in env_content:
            print("⚠️  ADMIN_IDS still has placeholder - Add your Telegram ID")
        else:
            print("✅ ADMIN_IDS appears to be configured")
    else:
        print("❌ .env file not found - Run: cp .env.example .env")
    
    print("\n" + "="*70)
