# NanoToolz Critical Patches

## PATCH 1: Fix Race Condition in Stock Depletion

**File:** `src/database/json_db.py`

```python
def pop_stock_atomic(self, product_id: int, count: int) -> list[str] | None:
    """Atomically reserve and pop stock. Returns None if insufficient stock."""
    pid = str(product_id)
    if pid not in self.stock:
        return None
    
    if len(self.stock[pid]) < count:
        return None  # Fail atomically - don't partially deduct
    
    items = self.stock[pid][:count]
    del self.stock[pid][:count]
    self.save_stock()
    return items
```

**File:** `src/bot/features/checkout/handlers.py` - Update `process_payment_credits()`:

```python
# Before deducting balance, validate ALL stock is available
for item in purchased_items:
    keys = db.pop_stock_atomic(item['product']['id'], item['qty'])
    if keys is None:
        await callback.answer(f"❌ {item['product']['name']} sold out!", show_alert=True)
        return
    # Store keys for later delivery
    item['keys'] = keys

# Only NOW deduct balance
new_balance = user['balance'] - total_price
db.update_user(user_id, {"balance": new_balance})

# Deliver using pre-reserved keys
for item in purchased_items:
    delivery_msg += f"📦 **{item['product']['name']}**\n"
    for k in item['keys']:
        delivery_msg += f"key: `{k}`\n"
```

---

## PATCH 2: Fix Callback Data Size Violations

**File:** `src/bot/features/catalog/handlers.py` - Update `show_product_detail()`:

```python
@router.callback_query(F.data.startswith("prod_"))
async def show_product_detail(callback: CallbackQuery, state: FSMContext):
    try:
        prod_id = int(callback.data.split("_")[1])
    except (ValueError, IndexError):
        await callback.answer("❌ Invalid product", show_alert=True)
        return
    
    product = db.get_product(prod_id)
    if not product:
        await callback.answer("❌ Product not found", show_alert=True)
        return
    
    # Store product in FSM instead of callback_data
    await state.update_data(current_product_id=prod_id)
    
    stock = db.get_stock_count(prod_id)
    stock_status = f"✅ In Stock ({stock})" if stock > 0 else "❌ Out of Stock"
    
    text = (
        f"📦 **{product['name']}**\n\n"
        f"📝 {product.get('description', 'No description')}\n\n"
        f"💲 Price: **${product['price']}**\n"
        f"📊 Status: {stock_status}\n"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Add to Cart", callback_data=f"add_cart_{prod_id}")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data=f"cat_{product['category_id']}")],
    ])
    
    image_url = product.get("image_url")
    if image_url:
        try:
            await asyncio.wait_for(
                callback.message.delete(),
                timeout=5.0
            )
            await asyncio.wait_for(
                callback.message.answer_photo(
                    photo=image_url,
                    caption=text,
                    reply_markup=keyboard,
                    parse_mode="Markdown"
                ),
                timeout=10.0
            )
        except asyncio.TimeoutError:
            logger.error("Timeout sending product photo")
            await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Failed to send photo: {e}")
            await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    else:
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    
    await callback.answer()
```

---

## PATCH 3: Fix Unvalidated Callback Data Parsing

**File:** `src/bot/features/catalog/handlers.py` - Update `show_categories()` and `show_products()`:

```python
@router.callback_query(F.data.startswith("cat_"))
async def show_products(callback: CallbackQuery):
    try:
        parts = callback.data.split("_")
        if len(parts) < 2:
            raise ValueError("Invalid callback format")
        cat_id = int(parts[1])
        if cat_id < 1:
            raise ValueError("Invalid category ID")
    except (ValueError, IndexError):
        await callback.answer("❌ Invalid request", show_alert=True)
        return
    
    category = db.get_category(cat_id)
    if not category:
        await callback.answer("❌ Category not found", show_alert=True)
        return
    
    products = db.get_products(category_id=cat_id)
    
    if not products:
        text = f"🚫 No products found in **{category['name']}**"
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="⬅️ Back", callback_data="catalog_main")]]
        )
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
        return
    
    buttons = []
    for p in products:
        buttons.append([InlineKeyboardButton(
            text=f"📦 {p['name']} - ${p['price']}",
            callback_data=f"prod_{p['id']}"
        )])
    
    buttons.append([InlineKeyboardButton(text="⬅️ Back", callback_data="catalog_main")])
    
    await callback.message.edit_text(
        f"📂 **{category['name']}**\nSelect a product:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        parse_mode="Markdown"
    )
    await callback.answer()
```

---

## PATCH 4: Fix Admin Permission Check with FSM Cleanup

**File:** `src/bot/features/admin/handlers.py` - Update `receive_stock_keys()`:

```python
@router.message(StockStates.waiting_for_keys)
async def receive_stock_keys(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("❌ Unauthorized")
        await state.clear()
        return
    
    data = await state.get_data()
    prod_id = data.get('prod_id')
    
    if not prod_id:
        await message.answer("❌ Session expired")
        await state.clear()
        return
    
    keys = []
    if message.document:
        await message.answer("⚠️ File upload not fully implemented yet. Send text.")
        return
    elif message.text:
        keys = [k.strip() for k in message.text.split('\n') if k.strip()]
    
    if not keys:
        await message.answer("❌ No valid keys found.")
        return
    
    # Validate keys
    invalid_keys = []
    for key in keys:
        if len(key) < 3 or len(key) > 500:
            invalid_keys.append(key)
        elif not all(c.isprintable() for c in key):
            invalid_keys.append(key)
    
    if invalid_keys:
        await message.answer(f"❌ Invalid keys found: {invalid_keys[:3]}")
        return
    
    db.add_stock(prod_id, keys)
    await message.answer(f"✅ Added **{len(keys)}** keys to stock!")
    await state.clear()
```

---

## PATCH 5: Fix Missing Error Handling in Async Handlers

**File:** `src/bot/features/checkout/handlers.py` - Update `process_payment_credits()`:

```python
@router.callback_query(F.data == "pay_credits")
async def process_payment_credits(callback: CallbackQuery):
    try:
        user_id = callback.from_user.id
        user = db.get_user(user_id)
        cart = user.get("cart", {})
        
        if not cart:
            await callback.answer("Cart expired", show_alert=True)
            return
        
        # Validate all stock before proceeding
        total_price = 0
        purchased_items = []
        
        for pid_str, qty in cart.items():
            product = db.get_product(int(pid_str))
            if not product:
                await callback.answer(f"❌ Product not found", show_alert=True)
                return
            
            total_price += product['price'] * qty
            purchased_items.append({"product": product, "qty": qty})
        
        if user['balance'] < total_price:
            await callback.answer("❌ Insufficient balance!", show_alert=True)
            return
        
        # Reserve stock atomically
        for item in purchased_items:
            keys = db.pop_stock_atomic(item['product']['id'], item['qty'])
            if keys is None:
                await callback.answer(f"❌ {item['product']['name']} sold out!", show_alert=True)
                return
            item['keys'] = keys
        
        # Deduct balance
        new_balance = user['balance'] - total_price
        db.update_user(user_id, {"balance": new_balance, "cart": {}})
        
        # Deliver
        delivery_msg = "✅ **Order Processed Successfully!**\n\n"
        
        for item in purchased_items:
            prod = item['product']
            delivery_msg += f"📦 **{prod['name']}**\n"
            for k in item['keys']:
                delivery_msg += f"key: `{k}`\n"
            delivery_msg += "\n"
            
            db.create_order({
                "user_id": user_id,
                "product_id": prod['id'],
                "qty": item['qty'],
                "total": prod['price'] * item['qty'],
                "keys_delivered": item['keys'],
                "timestamp": time.time()
            })
        
        delivery_msg += f"💰 New Balance: ${new_balance:.2f}\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Back to Home", callback_data="back_main")]
        ])
        
        await callback.message.edit_text(
            delivery_msg,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        await callback.answer("✅ Order Complete!")
        
        logger.info(f"Order completed: user={user_id}, total=${total_price}, items={len(purchased_items)}")
        
    except Exception as e:
        logger.error(f"Error in process_payment_credits: {e}", exc_info=True)
        await callback.answer("❌ Payment processing failed. Contact support.", show_alert=True)
```

---

## PATCH 6: Add Rate Limiting to Checkout

**File:** `src/bot/features/checkout/handlers.py` - Add at top:

```python
from src.middleware.rate_limiter import check_rate_limit

@router.callback_query(F.data == "checkout_start")
async def start_checkout(callback: CallbackQuery):
    if not check_rate_limit(callback.from_user.id):
        await callback.answer("⏱️ Too many requests. Wait a moment.", show_alert=True)
        return
    
    # ... rest of handler
```

---

## PATCH 7: Add Maintenance Mode Check

**File:** `src/bot/features/start/handlers.py` - Add helper:

```python
def is_maintenance_mode() -> bool:
    return db.settings.get("maintenance", False)

@router.callback_query(F.data == "checkout_start")
async def start_checkout(callback: CallbackQuery):
    if is_maintenance_mode():
        await callback.answer("🔧 Bot under maintenance. Try again later.", show_alert=True)
        return
    # ... rest
```

---

## PATCH 8: Add Graceful Shutdown

**File:** `src/bot/app.py`:

```python
import signal

async def start_bot():
    """Initialize and start the bot"""
    bot = Bot(token=settings.BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.update.outer_middleware(TypingMiddleware())
    setup_routers(dp)
    
    await bot.delete_webhook(drop_pending_updates=True)
    
    def signal_handler(sig, frame):
        print("\n🛑 Shutting down gracefully...")
        raise KeyboardInterrupt()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        print("🤖 Bot is running with JSON Database & High-Level UX...")
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        print("Saving data...")
    finally:
        # Flush all pending saves
        db.save_users()
        db.save_products()
        db.save_orders()
        db.save_stock()
        db.save_settings()
        await bot.session.close()
        print("✅ Bot stopped cleanly")
```

---

## PATCH 9: Add Input Validation for Product Price

**File:** `src/bot/features/admin/handlers.py` - Update `product_price_received()`:

```python
@router.message(ProductStates.waiting_for_price)
async def product_price_received(message: Message, state: FSMContext):
    try:
        price = float(message.text)
        if price <= 0 or price > 100000:
            await message.answer("❌ Price must be between $0.01 and $100,000")
            return
    except ValueError:
        await message.answer("❌ Invalid price format. Enter a number like 10.99")
        return
    
    data = await state.get_data()
    new_prod = {
        "name": data['name'],
        "price": price,
        "category_id": 1,
        "description": "No description",
        "image_url": None,
        "stock_count": 0
    }
    
    prod_id = db.add_product(new_prod)
    await state.clear()
    
    await message.answer(
        f"✅ Product **{data['name']}** added with price ${price}!",
        reply_markup=admin_product_edit_keyboard(prod_id),
        parse_mode="Markdown"
    )
    
    logger.info(f"Product created: id={prod_id}, name={data['name']}, price=${price}")
```

---

## PATCH 10: Add Idempotency Check on Orders

**File:** `src/bot/features/checkout/handlers.py` - Add at module level:

```python
_processing_orders = {}

@router.callback_query(F.data == "checkout_start")
async def start_checkout(callback: CallbackQuery):
    user_id = callback.from_user.id
    
    # Prevent duplicate orders
    if user_id in _processing_orders:
        await callback.answer("⏳ Order already processing", show_alert=True)
        return
    
    _processing_orders[user_id] = True
    try:
        # ... rest of handler
    finally:
        _processing_orders.pop(user_id, None)
```

---

## PATCH 11: Fix Typing Middleware Latency

**File:** `src/bot/middleware/typing.py`:

```python
class TypingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        
        chat_id = None
        if isinstance(event, Message):
            chat_id = event.chat.id
        elif isinstance(event, CallbackQuery) and event.message:
            chat_id = event.message.chat.id
        
        # Only add typing for messages, not callbacks
        if chat_id and isinstance(event, Message):
            try:
                await event.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
                await asyncio.sleep(random.uniform(0.1, 0.3))
            except Exception:
                pass
        
        return await handler(event, data)
```

---

## PATCH 12: Add Database Backup

**File:** `src/database/json_db.py` - Add method:

```python
import shutil
from datetime import datetime

def backup_database(self):
    """Create timestamped backup of all JSON files"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join(self.data_dir, "backups")
        os.makedirs(backup_dir, exist_ok=True)
        
        for file_path in [self.users_file, self.products_file, self.orders_file, self.stock_file]:
            if os.path.exists(file_path):
                backup_path = os.path.join(backup_dir, f"{os.path.basename(file_path)}.{timestamp}")
                shutil.copy2(file_path, backup_path)
        
        print(f"✅ Database backed up to {timestamp}")
    except Exception as e:
        print(f"❌ Backup failed: {e}")
```

---

## PATCH 13: Add Logging to Critical Operations

**File:** `src/bot/features/checkout/handlers.py` - Add logger calls:

```python
from src.logger import logger

# In process_payment_credits():
logger.info(f"Checkout started: user={user_id}, items={len(purchased_items)}, total=${total_price}")
logger.info(f"Order completed: user={user_id}, order_id={order_id}, total=${total_price}")
logger.error(f"Checkout failed: user={user_id}, reason={str(e)}")
```

---

## PATCH 14: Add Timeout to Async Operations

**File:** `src/bot/features/catalog/handlers.py`:

```python
import asyncio

try:
    await asyncio.wait_for(callback.message.delete(), timeout=5.0)
    await asyncio.wait_for(
        callback.message.answer_photo(photo=image_url, ...),
        timeout=10.0
    )
except asyncio.TimeoutError:
    logger.error("Timeout sending product photo")
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
except Exception as e:
    logger.error(f"Error sending photo: {e}")
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
```

---

## PATCH 15: Add Timezone-Aware Timestamps

**File:** `src/bot/features/start/handlers.py`:

```python
from datetime import datetime, timezone

db.update_user(user_id, {
    "username": username,
    "first_name": first_name,
    "joined_at": datetime.now(timezone.utc).isoformat()
})
```

---

## Application Order

Apply patches in this order:

1. **PATCH 1** - Race condition fix (critical)
2. **PATCH 4** - Admin permission fix (critical)
3. **PATCH 5** - Error handling (critical)
4. **PATCH 3** - Callback validation (critical)
5. **PATCH 6** - Rate limiting (high)
6. **PATCH 9** - Input validation (high)
7. **PATCH 10** - Idempotency (high)
8. **PATCH 7** - Maintenance mode (high)
9. **PATCH 8** - Graceful shutdown (high)
10. **PATCH 11** - Typing middleware (high)
11. **PATCH 12** - Database backup (medium)
12. **PATCH 13** - Logging (medium)
13. **PATCH 14** - Timeouts (medium)
14. **PATCH 15** - Timestamps (medium)

---

**Total Lines Changed:** ~500
**Files Modified:** 8
**Estimated Time:** 2-3 hours
