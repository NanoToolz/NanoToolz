# NanoToolz Audit - Quick Reference Guide

## 🚨 CRITICAL ISSUES AT A GLANCE

### Issue 1: Race Condition (Stock Overselling)
**Where:** Checkout flow
**What:** Two users can buy the same item
**Fix:** Use `pop_stock_atomic()` instead of `pop_stock()`
**Time:** 30 min
**Priority:** 🔴 CRITICAL

### Issue 2: Callback Data Size
**Where:** Product buttons
**What:** Buttons fail if callback_data > 64 bytes
**Fix:** Use FSM context instead of callback_data
**Time:** 45 min
**Priority:** 🔴 CRITICAL

### Issue 3: Unvalidated Callback Parsing
**Where:** All handlers with `callback.data.split()`
**What:** Bot crashes on malformed data
**Fix:** Add try/except and bounds checking
**Time:** 30 min
**Priority:** 🔴 CRITICAL

### Issue 4: Admin Permission Check
**Where:** `receive_stock_keys()` handler
**What:** FSM state hangs if non-admin accesses
**Fix:** Add `await state.clear()` on unauthorized
**Time:** 15 min
**Priority:** 🔴 CRITICAL

### Issue 5: Blocking I/O
**Where:** `process_payment_mock()` - `time.sleep(1)`
**What:** Bot freezes for all users
**Fix:** Use `await asyncio.sleep(1)`
**Time:** ✅ ALREADY FIXED
**Priority:** 🔴 CRITICAL

### Issue 6: Missing Error Handling
**Where:** Async operations (delete, send_photo)
**What:** Silent failures, poor debugging
**Fix:** Add specific exception handling
**Time:** 45 min
**Priority:** 🔴 CRITICAL

### Issue 7: Database Inconsistency
**Where:** JSON vs SQLAlchemy models
**What:** Data duplication, lost transactions
**Fix:** Choose one database system
**Time:** 2 hours
**Priority:** 🔴 CRITICAL

### Issue 8: No Transaction Rollback
**Where:** Checkout payment processing
**What:** Balance deducted but no keys delivered
**Fix:** Validate all stock before deducting
**Time:** 45 min
**Priority:** 🔴 CRITICAL

### Issue 9: Callback Answer Not Awaited
**Where:** Multiple handlers
**What:** Notifications may not show
**Fix:** Add `await` to all `callback.answer()` calls
**Time:** 15 min
**Priority:** 🔴 CRITICAL

### Issue 10: No Rate Limiting
**Where:** Checkout handler
**What:** Users can spam checkout, duplicate orders
**Fix:** Add `check_rate_limit()` call
**Time:** 20 min
**Priority:** 🔴 CRITICAL

---

## 🔧 QUICK FIX CHECKLIST

### Checkout Flow (Most Critical)
```python
# ❌ BEFORE
@router.callback_query(F.data == "checkout_start")
async def start_checkout(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = db.get_user(user_id)
    cart = user.get("cart", {})
    
    # Deduct balance immediately
    new_balance = user['balance'] - total_price
    db.update_user(user_id, {"balance": new_balance})
    
    # Then try to deliver (might fail!)
    for item in purchased_items:
        keys = db.pop_stock(item['product']['id'], item['qty'])

# ✅ AFTER
@router.callback_query(F.data == "checkout_start")
async def start_checkout(callback: CallbackQuery):
    if not check_rate_limit(callback.from_user.id):
        await callback.answer("Too many requests", show_alert=True)
        return
    
    user_id = callback.from_user.id
    user = db.get_user(user_id)
    cart = user.get("cart", {})
    
    # VALIDATE ALL STOCK FIRST
    for pid_str, qty in cart.items():
        keys = db.pop_stock_atomic(int(pid_str), qty)
        if keys is None:
            await callback.answer("Stock sold out!", show_alert=True)
            return
    
    # ONLY THEN deduct balance
    new_balance = user['balance'] - total_price
    db.update_user(user_id, {"balance": new_balance})
```

### Callback Data Validation
```python
# ❌ BEFORE
cat_id = int(callback.data.split("_")[1])  # Crashes!

# ✅ AFTER
try:
    parts = callback.data.split("_")
    if len(parts) < 2:
        raise ValueError("Invalid format")
    cat_id = int(parts[1])
    if cat_id < 1:
        raise ValueError("Invalid ID")
except (ValueError, IndexError):
    await callback.answer("Invalid request", show_alert=True)
    return
```

### Admin Permission Check
```python
# ❌ BEFORE
@router.message(StockStates.waiting_for_keys)
async def receive_stock_keys(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return  # FSM state NOT cleared!

# ✅ AFTER
@router.message(StockStates.waiting_for_keys)
async def receive_stock_keys(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("Unauthorized")
        await state.clear()  # Clear FSM state!
        return
```

### Error Handling
```python
# ❌ BEFORE
try:
    await callback.message.delete()
    await callback.message.answer_photo(...)
except Exception:
    await callback.message.answer(text)  # Swallows error!

# ✅ AFTER
try:
    await asyncio.wait_for(callback.message.delete(), timeout=5.0)
    await asyncio.wait_for(
        callback.message.answer_photo(...),
        timeout=10.0
    )
except asyncio.TimeoutError:
    logger.error("Timeout sending photo")
    await callback.message.edit_text(text, ...)
except Exception as e:
    logger.error(f"Error: {e}")
    await callback.answer("Failed to load image", show_alert=True)
```

---

## 📊 SEVERITY MATRIX

```
┌─────────────────────────────────────────────────────────┐
│ SEVERITY │ COUNT │ FIX TIME │ MUST FIX │ IMPACT        │
├─────────────────────────────────────────────────────────┤
│ CRITICAL │  10   │ 3-4 hrs  │ YES      │ Data loss     │
│ HIGH     │  10   │ 3-4 hrs  │ YES      │ Crashes       │
│ MEDIUM   │  10   │ 3-4 hrs  │ SOON     │ UX issues     │
│ LOW      │   5   │ 1-2 hrs  │ NO       │ Minor issues  │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 PRIORITY ORDER

### Day 1 (Critical - 4 hours)
1. ✅ Fix race condition (PATCH 1)
2. ✅ Fix admin permission (PATCH 4)
3. ✅ Fix error handling (PATCH 5)
4. ✅ Fix callback validation (PATCH 3)
5. ✅ Add rate limiting (PATCH 6)

### Day 2 (High - 4 hours)
6. ✅ Fix input validation (PATCH 9)
7. ✅ Add idempotency (PATCH 10)
8. ✅ Add maintenance mode (PATCH 7)
9. ✅ Add graceful shutdown (PATCH 8)
10. ✅ Fix typing middleware (PATCH 11)

### Day 3 (Medium - 4 hours)
11. ✅ Add database backup (PATCH 12)
12. ✅ Add logging (PATCH 13)
13. ✅ Add timeouts (PATCH 14)
14. ✅ Add timestamps (PATCH 15)
15. ✅ Consolidate database

### Day 4 (Testing - 4 hours)
16. ✅ Run test suite
17. ✅ Load testing
18. ✅ Manual testing
19. ✅ Security review

---

## 🧪 QUICK TEST COMMANDS

```bash
# Test race condition
pytest tests/test_checkout_race_condition.py -v

# Test callback validation
pytest tests/test_callback_validation.py -v

# Test admin permissions
pytest tests/test_admin_permissions.py -v

# Test payment rollback
pytest tests/test_payment_rollback.py -v

# Test database consistency
pytest tests/test_db_consistency.py -v

# Run all tests
pytest tests/ -v --cov=src

# Load test
pytest tests/test_performance.py -v
```

---

## 📝 COMMIT MESSAGE TEMPLATE

```
fix: [ISSUE_NUMBER] - [BRIEF_DESCRIPTION]

Fixes #[ISSUE_NUMBER]

Changes:
- [CHANGE 1]
- [CHANGE 2]
- [CHANGE 3]

Testing:
- [TEST 1]
- [TEST 2]

Verification:
- [x] No race conditions
- [x] All inputs validated
- [x] Error handling in place
- [x] Tests passing
```

---

## 🚀 DEPLOYMENT CHECKLIST

Before deploying to production:

- [ ] All critical issues fixed
- [ ] All high priority issues fixed
- [ ] Test suite passes 100%
- [ ] Load test with 100+ concurrent users succeeds
- [ ] Database backups working
- [ ] Logging configured
- [ ] Monitoring alerts set up
- [ ] Rollback plan documented
- [ ] Admin trained on new features
- [ ] Support team briefed

---

## 🆘 TROUBLESHOOTING

### Bot crashes on checkout
**Cause:** Unhandled exception in payment processing
**Fix:** Check logs, add try/except, apply PATCH 5

### Buttons don't work
**Cause:** Callback data too large or malformed
**Fix:** Validate callback_data, apply PATCH 2 & 3

### FSM state hangs
**Cause:** Non-admin enters FSM, state not cleared
**Fix:** Add `await state.clear()`, apply PATCH 4

### Duplicate orders
**Cause:** User clicks checkout twice
**Fix:** Add rate limiting and idempotency, apply PATCH 6 & 10

### Data loss on shutdown
**Cause:** No graceful shutdown
**Fix:** Add shutdown handler, apply PATCH 8

### Slow bot response
**Cause:** Typing middleware adds latency
**Fix:** Reduce delay or remove for callbacks, apply PATCH 11

### Stock overselling
**Cause:** Race condition in concurrent checkout
**Fix:** Use atomic operations, apply PATCH 1

---

## 📚 DOCUMENTATION LINKS

- **Full Audit:** `EXHAUSTIVE_AUDIT_REPORT.md`
- **Code Patches:** `CRITICAL_PATCHES.md`
- **Test Plan:** `TEST_PLAN.md`
- **Summary:** `AUDIT_SUMMARY.md`
- **This Guide:** `QUICK_REFERENCE.md`

---

## 💡 KEY TAKEAWAYS

1. **Always validate input** - Never trust user data
2. **Use atomic operations** - Stock depletion must be atomic
3. **Add error handling** - Every async operation needs try/except
4. **Test concurrency** - Race conditions are hard to spot
5. **Single database** - Don't mix multiple database systems
6. **Transaction semantics** - Validate before deducting
7. **Rate limiting** - Prevent spam and duplicate orders
8. **Logging** - Essential for debugging
9. **Graceful shutdown** - Save data on exit
10. **Test coverage** - Catch issues before production

---

**Quick Reference Created:** 2026-01-25
**Last Updated:** 2026-01-25
**Version:** 1.0
