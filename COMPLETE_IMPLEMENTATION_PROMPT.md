# COMPLETE COMPREHENSIVE PROMPT FOR AI AGENT
## NanoToolz Telegram E-Commerce Bot v2.0 - Full Implementation Guide

================================================================================
PART E: DAILY PRICE UPDATE SCHEDULER (CONTINUED)
================================================================================

E1. CREATE SCHEDULER
    Create: src/scheduler.py
    
    ```python
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from datetime import datetime
    from src.database import SessionLocal
    from src.database.models import Product
    from src.logger import logger
    
    scheduler = AsyncIOScheduler()
    
    async def update_prices_job():
        """Run daily at midnight UTC"""
        db = SessionLocal()
        try:
            products = db.query(Product).all()
            
            for product in products:
                if product.price_drop_per_day_usd > 0:
                    # Recalculate days_until_minimum
                    days_elapsed = (datetime.utcnow() - product.created_at).days
                    days_until_min = max(0, product.drop_period_days - days_elapsed)
                    product.days_until_minimum = days_until_min
                    product.price_last_calculated = datetime.utcnow()
            
            db.commit()
            logger.info(f"✅ Daily price update completed for {len(products)} products")
        except Exception as e:
            logger.error(f"❌ Price update failed: {str(e)}")
            db.rollback()
        finally:
            db.close()
    
    def start_scheduler():
        """Start background scheduler"""
        scheduler.add_job(
            update_prices_job,
            'cron',
            hour=0,
            minute=0,
            id='daily_price_update',
            name='Daily Price Update'
        )
        scheduler.start()
        logger.info("🕐 Scheduler started - Daily price update at 00:00 UTC")
    
    def stop_scheduler():
        """Stop scheduler"""
        if scheduler.running:
            scheduler.shutdown()
            logger.info("🛑 Scheduler stopped")
    ```

E2. INTEGRATE SCHEDULER WITH BOT
    File: main.py
    
    Update:
    ```python
    import asyncio
    import logging
    from aiogram import Bot
    from src.config import settings
    from src.database import init_db
    from src.bot import create_dispatcher, set_bot_commands
    from src.seed import seed_dummy_data
    from src.scheduler import start_scheduler, stop_scheduler
    from src.logger import logger
    
    async def main():
        """Main bot entry point"""
        
        # Initialize database
        logger.info("🗄️  Initializing database...")
        init_db()
        
        # Seed dummy data
        logger.info("🌱 Seeding dummy data...")
        seed_dummy_data()
        
        # Start scheduler
        logger.info("⏰ Starting scheduler...")
        start_scheduler()
        
        # Create bot and dispatcher
        logger.info("🤖 Starting bot...")
        bot = Bot(token=settings.BOT_TOKEN)
        dp = create_dispatcher()
        
        # Set bot commands
        await set_bot_commands(bot)
        
        try:
            logger.info("✅ Bot started! Polling for updates...")
            await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
        except KeyboardInterrupt:
            logger.info("⏹️  Bot stopped by user")
        finally:
            stop_scheduler()
            await bot.session.close()
    
    if __name__ == "__main__":
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            logger.info("Bot interrupted")
    ```

================================================================================
PART F: COMPLETE FILE STRUCTURE
================================================================================

After implementation, your project should look like:

```
NanoToolz/
├── src/
│   ├── bot/
│   │   ├── features/
│   │   │   ├── start/
│   │   │   │   ├── handlers.py (WITH ERROR HANDLING)
│   │   │   │   ├── keyboards.py
│   │   │   │   └── messages.py
│   │   │   ├── catalog/
│   │   │   │   ├── handlers.py (WITH PRICING DISPLAY)
│   │   │   │   ├── keyboards.py
│   │   │   │   └── messages.py
│   │   │   ├── cart/
│   │   │   │   ├── handlers.py (WITH ERROR HANDLING)
│   │   │   │   ├── keyboards.py
│   │   │   │   └── messages.py
│   │   │   ├── checkout/
│   │   │   │   ├── handlers.py (WITH CURRENT PRICING)
│   │   │   │   ├── keyboards.py
│   │   │   │   └── messages.py
│   │   │   ├── profile/
│   │   │   │   ├── handlers.py (SHOW CREDITS)
│   │   │   │   ├── keyboards.py
│   │   │   │   └── messages.py
│   │   │   ├── wishlist/
│   │   │   ├── rewards/
│   │   │   ├── referral/
│   │   │   ├── support/
│   │   │   ├── topup/ (NEW FEATURE)
│   │   │   │   ├── handlers.py
│   │   │   │   ├── keyboards.py
│   │   │   │   └── messages.py
│   │   │   └── help/
│   │   ├── common/
│   │   │   └── keyboards.py (UPDATED WITH TOPUP BUTTON)
│   │   ├── app.py
│   │   ├── commands.py
│   │   └── routers.py (FIXED - NO DUPLICATE)
│   ├── database/
│   │   ├── __init__.py
│   │   └── models.py (UPDATED WITH PRICING FIELDS)
│   ├── services/
│   │   ├── cart.py (UPDATED WITH CURRENT PRICING)
│   │   ├── orders.py (UPDATED WITH CURRENT PRICING)
│   │   ├── pricing.py (NEW - PRICING CALCULATIONS)
│   │   └── settings.py
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── error_handler.py (NEW)
│   │   └── rate_limiter.py (NEW)
│   ├── utils/
│   │   ├── __init__.py
│   │   └── validators.py (NEW)
│   ├── logger.py (NEW)
│   ├── scheduler.py (NEW)
│   ├── config.py
│   └── seed.py
├── web/
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── dashboard.py (NEW)
│   │   ├── products.py (NEW)
│   │   ├── pricing.py (NEW)
│   │   ├── categories.py (NEW)
│   │   ├── users.py (NEW)
│   │   ├── orders.py (NEW)
│   │   ├── payments.py (NEW)
│   │   ├── topups.py (NEW)
│   │   ├── settings.py (NEW)
│   │   ├── support.py (NEW)
│   │   └── analytics.py (NEW)
│   ├── auth.py (NEW)
│   └── admin.py (REFACTORED)
├── logs/
│   └── bot.log (AUTO-CREATED)
├── main.py (UPDATED)
├── requirements.txt (UPDATED)
├── .env
├── .env.example
├── .gitignore
├── README.md
└── ANALYSIS_REPORT.md
```

================================================================================
PART G: IMPLEMENTATION CHECKLIST
================================================================================

PHASE 1: CRITICAL FIXES (Do First)
- [ ] Fix duplicate start_router in routers.py
- [ ] Delete empty folders (handlers/, static/, templates/)
- [ ] Add error handling to all handlers
- [ ] Add input validation (validators.py)
- [ ] Add logging system (logger.py)
- [ ] Add rate limiting (rate_limiter.py)

PHASE 2: PRICING SYSTEM
- [ ] Update Product model with pricing fields
- [ ] Create pricing.py service
- [ ] Update catalog handlers to show pricing
- [ ] Update cart service to use current pricing
- [ ] Update checkout to lock price
- [ ] Create scheduler for daily updates

PHASE 3: TOPUP FEATURE
- [ ] Create topup feature folder
- [ ] Create topup handlers
- [ ] Create topup keyboards
- [ ] Create topup messages
- [ ] Register topup router
- [ ] Add topup button to main menu
- [ ] Update profile to show credits
- [ ] Update checkout to accept credits

PHASE 4: ADMIN PANEL
- [ ] Create auth.py for authentication
- [ ] Refactor admin.py into modular routes
- [ ] Create dashboard route
- [ ] Create products route with pricing
- [ ] Create categories route
- [ ] Create users route
- [ ] Create orders route
- [ ] Create payments route
- [ ] Create topups route
- [ ] Create settings route
- [ ] Create support route
- [ ] Create analytics route

PHASE 5: TESTING & DEPLOYMENT
- [ ] Test bot startup
- [ ] Test all handlers for errors
- [ ] Test rate limiting
- [ ] Test pricing calculations
- [ ] Test topup flow
- [ ] Test admin login
- [ ] Test admin product creation
- [ ] Test price drops daily
- [ ] Test checkout with credits
- [ ] Test logging

================================================================================
PART H: TESTING GUIDE
================================================================================

H1. TEST PRICING SYSTEM
    
    Test Case 1: Price Calculation
    - Add product: Initial $30, Drop 30 days, Min $5
    - Day 0: Should show $30
    - Day 7: Should show $24.17 (approx)
    - Day 30: Should show $5 (minimum)
    - Day 31: Should still show $5
    
    Test Case 2: Price Display
    - New product (< 1 day): Show only current price
    - Dropping product (1-29 days): Show strikethrough + discount %
    - At minimum (>= 30 days): Show "MINIMUM" label
    
    Test Case 3: Cart Pricing
    - Add product to cart
    - Price should be CURRENT price, not initial
    - Change date, refresh, price should update
    
    Test Case 4: Checkout Lock
    - Add to cart at $20
    - Wait 1 day (price drops to $19)
    - Checkout should still charge $20 (locked price)

H2. TEST TOPUP SYSTEM
    
    Test Case 1: Topup Flow
    - Click "Top Up" button
    - Select $10
    - Receive payment instructions
    - Click "I Paid"
    - Credits should be added
    - Profile should show new balance
    
    Test Case 2: Topup Payment
    - Create topup payment
    - Verify payment_ref is unique
    - Verify amount is correct
    - Verify wallet is correct
    
    Test Case 3: Use Credits
    - Topup $50
    - Add product ($30) to cart
    - Checkout with credits
    - Credits should be deducted
    - Order should be completed

H3. TEST ADMIN PANEL
    
    Test Case 1: Admin Login
    - Go to /admin
    - Login with wrong credentials → Should fail
    - Login with correct credentials → Should succeed
    
    Test Case 2: Add Product with Pricing
    - Go to /admin/products
    - Click "Add Product"
    - Fill: Name, Category, Initial Price $30, Drop 30 days, Min $5
    - Submit
    - Product should appear in list
    - Pricing should be set correctly
    
    Test Case 3: Edit Pricing
    - Go to /admin/pricing
    - Select product
    - Change drop period to 60 days
    - Save
    - Price drop rate should recalculate
    
    Test Case 4: View Analytics
    - Go to /admin/analytics
    - Should show revenue, users, orders
    - Should show charts

H4. TEST ERROR HANDLING
    
    Test Case 1: Database Error
    - Disconnect database
    - Try to add to cart
    - Should show user-friendly error
    - Should log error
    
    Test Case 2: Invalid Input
    - Send very long message to support
    - Should be truncated or rejected
    - Should show validation error
    
    Test Case 3: Rate Limiting
    - Send 15 requests in 10 seconds
    - After 5: Should warn
    - After 10: Should block
    - Should show cooldown message

H5. TEST LOGGING
    
    Check logs/bot.log for:
    - Bot startup message
    - User actions (add to cart, checkout, etc.)
    - Errors with full context
    - Daily price update message
    - Admin actions

================================================================================
PART I: DEPLOYMENT INSTRUCTIONS
================================================================================

I1. BEFORE DEPLOYMENT
    
    1. Update requirements.txt:
    ```
    aiogram==3.3.0
    python-dotenv==1.0.0
    sqlalchemy==2.0.23
    fastapi==0.109.0
    uvicorn==0.27.0
    pydantic==2.5.0
    pydantic-settings==2.1.0
    APScheduler==3.10.4
    ```
    
    2. Create .env file:
    ```
    BOT_TOKEN=your_bot_token_here
    ADMIN_IDS=123456789
    DATABASE_URL=sqlite:///nanotoolz.db
    ADMIN_USERNAME=admin
    ADMIN_PASSWORD=your_secure_password
    PAYMENT_WALLET_TRON=your_tron_wallet
    PAYMENT_WALLET_LTC=your_ltc_wallet
    DEBUG=False
    APP_ENV=production
    ```
    
    3. Create logs/ folder:
    ```bash
    mkdir -p logs
    ```
    
    4. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

I2. RUN BOT
    
    Development:
    ```bash
    python main.py
    ```
    
    Production (with systemd):
    ```bash
    # Create /etc/systemd/system/nanotoolz.service
    [Unit]
    Description=NanoToolz Telegram Bot
    After=network.target
    
    [Service]
    Type=simple
    User=nanotoolz
    WorkingDirectory=/home/nanotoolz/NanoToolz
    ExecStart=/usr/bin/python3 /home/nanotoolz/NanoToolz/main.py
    Restart=always
    RestartSec=10
    
    [Install]
    WantedBy=multi-user.target
    ```
    
    Then:
    ```bash
    sudo systemctl start nanotoolz
    sudo systemctl enable nanotoolz
    ```

I3. RUN ADMIN PANEL
    
    Development:
    ```bash
    uvicorn web.admin:app --reload --host 0.0.0.0 --port 8000
    ```
    
    Production:
    ```bash
    uvicorn web.admin:app --host 0.0.0.0 --port 8000 --workers 4
    ```
    
    Access: http://localhost:8000

I4. MONITOR LOGS
    
    ```bash
    tail -f logs/bot.log
    ```

================================================================================
PART J: IMPORTANT NOTES & WARNINGS
================================================================================

J1. DATABASE MIGRATION
    - Existing products will need pricing fields populated
    - Set price_initial_usd = current price_usd
    - Set price_drop_per_day_usd = 0 (no drop for old products)
    - Set price_minimum_usd = price_usd (no minimum)

J2. PRICE CALCULATION ACCURACY
    - Use DECIMAL type for prices (not float)
    - Round to 2 decimal places
    - Always use current price in cart/checkout
    - Lock price at payment time

J3. TIMEZONE HANDLING
    - Use UTC for all timestamps
    - Scheduler runs at 00:00 UTC
    - Convert to user's timezone for display (optional)

J4. SECURITY
    - Never expose admin password in logs
    - Use HTTPS in production
    - Validate all user inputs
    - Sanitize database queries
    - Use environment variables for secrets

J5. PERFORMANCE
    - Cache product prices (update daily)
    - Use database indexes on frequently queried fields
    - Limit query results (pagination)
    - Use connection pooling

J6. BACKUP
    - Backup database daily
    - Keep 7 days of backups
    - Test restore procedure

================================================================================
PART K: TROUBLESHOOTING
================================================================================

K1. BOT NOT STARTING
    - Check BOT_TOKEN in .env
    - Check database connection
    - Check logs/bot.log for errors
    - Verify all imports are correct

K2. PRICES NOT UPDATING
    - Check scheduler is running
    - Check logs for scheduler errors
    - Verify cron job is set correctly
    - Check database has pricing fields

K3. ADMIN PANEL NOT LOADING
    - Check admin credentials
    - Check database connection
    - Check port 8000 is not in use
    - Check logs for FastAPI errors

K4. TOPUP NOT WORKING
    - Check payment wallet is set
    - Check user has topup router registered
    - Check database has credits field
    - Check payment confirmation logic

K5. RATE LIMITING TOO STRICT
    - Adjust limit in rate_limiter.py
    - Change from 10 to 20 requests per minute
    - Adjust warning threshold

================================================================================
PART L: FINAL CHECKLIST BEFORE DEPLOYMENT
================================================================================

Code Quality:
- [ ] All handlers have error handling
- [ ] All inputs are validated
- [ ] All database operations use try-except
- [ ] No hardcoded values (use config)
- [ ] No print statements (use logger)
- [ ] Code follows PEP 8 style

Functionality:
- [ ] Bot starts without errors
- [ ] All 10 features work
- [ ] Pricing calculates correctly
- [ ] Topup system works
- [ ] Admin panel works
- [ ] Scheduler runs daily
- [ ] Logging works

Security:
- [ ] Admin password is secure
- [ ] No credentials in code
- [ ] Input validation works
- [ ] Rate limiting works
- [ ] Database is backed up

Performance:
- [ ] Bot responds quickly
- [ ] No memory leaks
- [ ] Database queries are optimized
- [ ] Scheduler doesn't block bot

Documentation:
- [ ] README.md is updated
- [ ] Code has comments where needed
- [ ] Error messages are clear
- [ ] Admin panel is intuitive

================================================================================
PART M: SUMMARY OF CHANGES
================================================================================

NEW FILES CREATED:
1. src/logger.py - Logging system
2. src/scheduler.py - Daily price updates
3. src/services/pricing.py - Pricing calculations
4. src/utils/validators.py - Input validation
5. src/middleware/rate_limiter.py - Rate limiting
6. src/middleware/error_handler.py - Error handling
7. src/bot/features/topup/ - Topup feature (3 files)
8. web/auth.py - Admin authentication
9. web/routes/ - Admin panel routes (10 files)

FILES MODIFIED:
1. src/database/models.py - Add pricing fields
2. src/bot/routers.py - Fix duplicate, add topup
3. src/bot/features/catalog/handlers.py - Show pricing
4. src/bot/features/cart/handlers.py - Add error handling
5. src/bot/features/checkout/handlers.py - Use current pricing
6. src/bot/features/profile/handlers.py - Show credits
7. src/bot/common/keyboards.py - Add topup button
8. src/services/cart.py - Use current pricing
9. src/services/orders.py - Use current pricing
10. main.py - Add scheduler
11. web/admin.py - Refactor into routes
12. requirements.txt - Add APScheduler

FILES DELETED:
1. src/handlers/ (empty folder)
2. web/static/ (empty folder)
3. web/templates/ (empty folder)

================================================================================
PART N: ESTIMATED TIMELINE
================================================================================

Phase 1 (Critical Fixes): 2-3 hours
Phase 2 (Pricing System): 4-5 hours
Phase 3 (Topup Feature): 3-4 hours
Phase 4 (Admin Panel): 6-8 hours
Phase 5 (Testing): 3-4 hours

TOTAL: 18-24 hours of development

================================================================================
PART O: SUPPORT & MAINTENANCE
================================================================================

After deployment:
1. Monitor logs daily
2. Check price updates run daily
3. Backup database daily
4. Update bot token if needed
5. Add new products as needed
6. Monitor admin panel usage
7. Handle user support tickets
8. Track revenue and analytics

================================================================================
END OF COMPLETE PROMPT
================================================================================

This prompt is now COMPLETE and ready for AI agent implementation.
All sections are detailed with code examples and clear instructions.
```
