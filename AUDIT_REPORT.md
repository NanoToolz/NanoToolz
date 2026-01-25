# 🛡️ NanoToolz Bot - Brutal Audit Report

**Overall Health:** ⚠️ **CRITICAL RISKS DETECTED**
The bot is functionally complete but **NOT production-ready**. It suffers from severe blocking I/O issues that will freeze the bot under load, critical security flaws in admin handlers (missing auth checks), and logic exploits (negative top-ups). The JSON database implementation, while simple, is synchronous and will causing the event loop to block.

---

## 🚨 Findings List

### 1. 🔴 CRITICAL: Blocking I/O in Async Loop
*   **File:** `src/database/json_db.py` (All methods)
*   **Issue:** `json.load` and `json.dump` are blocking synchronous operations. `db.save_users()` writes the entire file to disk.
*   **Impact:** When a user buys an item or updates profile, the ENTIRE bot freezes for all other users until the disk write completes. As file size grows (orders, logs), the bot will become unresponsive.
*   **Fix:** Offload JSON read/write to `asyncio.to_thread` or use `aiofiles`.

### 2. 🔴 CRITICAL: Admin Handler Auth Bypass
*   **File:** `src/bot/features/admin/handlers.py` (callbacks like `add_product`, `delete_product`)
*   **Issue:** Only the entry point `/admin` commands check `is_admin`. The specific state-setting callbacks (`add_product`, `edit_prod_...`) DO NOT check if the user is an admin.
*   **Exploit:** A persistent attacker can send a callback event with `data="add_product"` and trigger the product addition wizard even if they are not an admin.
*   **Fix:** Add `if not is_admin(callback.from_user.id): return` to EVERY admin callback handler.

### 3. 🔴 CRITICAL: Negative Amount Exploit
*   **File:** `src/bot/features/topup/handlers.py`
*   **Issue:** `amount = int(parts[2])` blindly trusts the callback data.
*   **Exploit:** An attacker can manually trigger `pay_crypto_-1000`. The code adds this to balance: `balance + (-1000)`. Balance decreases.
*   **Fix:** Validate `amount > 0` before processing.

### 4. 🟠 HIGH: Race Condition / No Pagination in Lists
*   **File:** `src/bot/features/admin/handlers.py`, `src/bot/features/catalog/handlers.py`
*   **Issue:** `admin_products_keyboard` lists ALL products. Telegram limits inline keyboards.
*   **Impact:** If you have >50-100 products, the message will fail to send (Button limit or Message too long).
*   **Fix:** Implement pagination (Pages 1, 2, 3...) for product lists.

### 5. 🟡 MEDIUM: O(N) Order History Scan
*   **File:** `src/bot/features/profile/handlers.py`
*   **Issue:** `[o for o in db.orders if ...]` scans the entire global order history every time a user views their profile.
*   **Impact:** Performance degradation as order history grows.
*   **Fix:** Store `order_ids` in `users.json` for O(1) access, or index orders.

---

## 🛠️ Patches (Top Issues)

### Patch 1: Fix Admin Auth Bypass
**Target:** `src/bot/features/admin/handlers.py`
```python
# Add this decorator or check to all handlers
def admin_required(func):
    async def wrapper(event, *args, **kwargs):
        user_id = event.from_user.id
        if not is_admin(user_id):
            return
        return await func(event, *args, **kwargs)
    return wrapper

# Apply to handlers:
@router.callback_query(F.data == "add_product")
async def start_add_product(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id): return # <--- FIX
    # ... rest of code
```

### Patch 2: Non-Blocking JSON DB
**Target:** `src/database/json_db.py`
```python
import asyncio

# Rename methods to async
async def save_users(self):
    await asyncio.to_thread(self._save_json, self.users_file, self.users)

# Update callers
# await db.save_users() 
```

### Patch 3: Negative Topup Fix
**Target:** `src/bot/features/topup/handlers.py`
```python
@router.callback_query(F.data.startswith("pay_"))
async def process_mock_topup(callback: CallbackQuery):
    # ...
    amount = int(parts[2])
    if amount <= 0: return # <--- FIX
    # ...
```

---

## 🧪 Test Plan

### Test Case 1: Admin Auth
1. Get a non-admin user ID.
2. Send a manual callback update with `data="add_product"`.
3. **Expect:** Bot ignores request or answers "Unauthorized".
4. **Current:** Bot asks for product name.

### Test Case 2: Negative Topup
1. Send callback `data="pay_crypto_-500"`.
2. **Expect:** Transaction fails or nothing happens.
3. **Current:** Balance reduced by 500.

### Test Case 3: Load Test
1. Create dummy `products.json` with 10,000 items.
2. Trigger `/start` or `Catalog`.
3. **Expect:** Bot responds instantly.
4. **Current:** Bot likely hangs reading large JSON on main thread.