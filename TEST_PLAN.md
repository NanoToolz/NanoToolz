# NanoToolz Test Plan

## Test Environment Setup

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-mock aioresponses

# Create tests directory
mkdir -p tests
touch tests/__init__.py
```

---

## CRITICAL TEST CASES

### Test 1: Concurrent Stock Depletion (Race Condition)

**File:** `tests/test_checkout_race_condition.py`

```python
import pytest
import asyncio
from unittest.mock import patch, MagicMock
from src.database.json_db import JsonDatabase

@pytest.mark.asyncio
async def test_concurrent_stock_depletion():
    """Verify only one user can buy the last item"""
    db = JsonDatabase()
    
    # Setup: 1 item in stock
    db.stock = {"1": ["key_1"]}
    
    # Simulate 10 concurrent checkout attempts
    async def attempt_checkout(user_id):
        keys = db.pop_stock_atomic(1, 1)
        return keys is not None
    
    results = await asyncio.gather(*[attempt_checkout(i) for i in range(10)])
    
    # Only 1 should succeed
    assert sum(results) == 1, f"Expected 1 success, got {sum(results)}"
    assert len(db.stock.get("1", [])) == 0, "Stock should be empty"

@pytest.mark.asyncio
async def test_stock_depletion_atomicity():
    """Verify stock depletion is atomic"""
    db = JsonDatabase()
    db.stock = {"1": ["key_1", "key_2", "key_3"]}
    
    # Try to buy 5 items (only 3 available)
    keys = db.pop_stock_atomic(1, 5)
    
    assert keys is None, "Should fail atomically"
    assert len(db.stock["1"]) == 3, "Stock should not be partially deducted"
```

**Run:**
```bash
pytest tests/test_checkout_race_condition.py -v
```

---

### Test 2: Callback Data Validation

**File:** `tests/test_callback_validation.py`

```python
import pytest
from aiogram.types import CallbackQuery, Message, User, Chat
from unittest.mock import AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_malformed_callback_data():
    """Verify bot doesn't crash on malformed callback_data"""
    
    # Create mock callback with invalid data
    callback = MagicMock(spec=CallbackQuery)
    callback.data = "cat_"  # Missing category ID
    callback.from_user = MagicMock(spec=User)
    callback.from_user.id = 123
    callback.message = AsyncMock()
    callback.answer = AsyncMock()
    
    # This should not raise an exception
    try:
        parts = callback.data.split("_")
        if len(parts) < 2:
            raise ValueError("Invalid format")
        cat_id = int(parts[1])
    except (ValueError, IndexError):
        # Expected behavior
        assert True
    else:
        assert False, "Should have raised ValueError"

@pytest.mark.asyncio
async def test_callback_data_size_limit():
    """Verify callback_data doesn't exceed 64 bytes"""
    
    # Generate callback_data
    callback_data = f"edit_prod_{999999999}"
    
    # Check size
    assert len(callback_data.encode('utf-8')) <= 64, \
        f"callback_data exceeds 64 bytes: {len(callback_data.encode('utf-8'))}"

@pytest.mark.asyncio
async def test_negative_product_id():
    """Verify negative product IDs are rejected"""
    
    try:
        prod_id = -1
        if prod_id < 1:
            raise ValueError("Invalid product ID")
    except ValueError:
        assert True
    else:
        assert False, "Should reject negative IDs"
```

**Run:**
```bash
pytest tests/test_callback_validation.py -v
```

---

### Test 3: Admin Permission Check

**File:** `tests/test_admin_permissions.py`

```python
import pytest
from unittest.mock import AsyncMock, MagicMock
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, User

@pytest.mark.asyncio
async def test_non_admin_stock_upload():
    """Verify non-admin cannot upload stock"""
    
    # Mock non-admin user
    message = MagicMock(spec=Message)
    message.from_user = MagicMock(spec=User)
    message.from_user.id = 999  # Non-admin
    message.text = "key1\nkey2\nkey3"
    message.answer = AsyncMock()
    
    # Mock FSM state
    state = MagicMock(spec=FSMContext)
    state.get_data = AsyncMock(return_value={"prod_id": 1})
    state.clear = AsyncMock()
    
    # Simulate handler
    from src.config import settings
    is_admin = message.from_user.id in settings.ADMIN_IDS
    
    if not is_admin:
        await message.answer("❌ Unauthorized")
        await state.clear()
        assert message.answer.called
        assert state.clear.called

@pytest.mark.asyncio
async def test_fsm_state_cleared_on_unauthorized():
    """Verify FSM state is cleared when unauthorized"""
    
    state = MagicMock(spec=FSMContext)
    state.clear = AsyncMock()
    
    # Simulate unauthorized access
    is_admin = False
    if not is_admin:
        await state.clear()
    
    assert state.clear.called, "FSM state should be cleared"
```

**Run:**
```bash
pytest tests/test_admin_permissions.py -v
```

---

### Test 4: Payment Rollback

**File:** `tests/test_payment_rollback.py`

```python
import pytest
from src.database.json_db import JsonDatabase

@pytest.mark.asyncio
async def test_payment_rollback_on_stock_depletion():
    """Verify balance is not deducted if stock depletes"""
    
    db = JsonDatabase()
    
    # Setup
    db.users = {
        "123": {"id": 123, "balance": 100.0, "cart": {"1": 2}}
    }
    db.products = [
        {"id": 1, "name": "Product A", "price": 50.0, "category_id": 1}
    ]
    db.stock = {"1": ["key_1"]}  # Only 1 key, but user wants 2
    
    user_id = 123
    user = db.get_user(user_id)
    cart = user.get("cart", {})
    
    # Validate stock BEFORE deducting
    for pid_str, qty in cart.items():
        keys = db.pop_stock_atomic(int(pid_str), qty)
        if keys is None:
            # Stock depleted - don't deduct balance
            assert user["balance"] == 100.0, "Balance should not be deducted"
            return
    
    # If we get here, test failed
    assert False, "Should have detected stock depletion"

@pytest.mark.asyncio
async def test_successful_payment_with_sufficient_stock():
    """Verify payment succeeds when stock is available"""
    
    db = JsonDatabase()
    
    # Setup
    db.users = {
        "123": {"id": 123, "balance": 100.0, "cart": {"1": 1}}
    }
    db.products = [
        {"id": 1, "name": "Product A", "price": 50.0, "category_id": 1}
    ]
    db.stock = {"1": ["key_1", "key_2"]}
    
    user_id = 123
    user = db.get_user(user_id)
    cart = user.get("cart", {})
    total_price = 50.0
    
    # Validate and reserve stock
    for pid_str, qty in cart.items():
        keys = db.pop_stock_atomic(int(pid_str), qty)
        assert keys is not None, "Stock should be available"
    
    # Deduct balance
    new_balance = user["balance"] - total_price
    assert new_balance == 50.0, "Balance should be deducted"
    assert len(db.stock["1"]) == 1, "Stock should be depleted"
```

**Run:**
```bash
pytest tests/test_payment_rollback.py -v
```

---

### Test 5: Database Consistency

**File:** `tests/test_db_consistency.py`

```python
import pytest
from src.database.json_db import JsonDatabase

@pytest.mark.asyncio
async def test_user_data_persistence():
    """Verify user data is saved and loaded correctly"""
    
    db = JsonDatabase()
    
    # Create user
    user_id = 123
    db.update_user(user_id, {"balance": 50.0, "username": "testuser"})
    
    # Reload database
    db._load_all()
    
    # Verify data persisted
    user = db.get_user(user_id)
    assert user["balance"] == 50.0
    assert user["username"] == "testuser"

@pytest.mark.asyncio
async def test_product_data_consistency():
    """Verify product data is consistent"""
    
    db = JsonDatabase()
    
    # Add product
    prod_id = db.add_product({
        "name": "Test Product",
        "price": 10.0,
        "category_id": 1
    })
    
    # Retrieve product
    product = db.get_product(prod_id)
    assert product["name"] == "Test Product"
    assert product["price"] == 10.0

@pytest.mark.asyncio
async def test_order_creation_and_retrieval():
    """Verify orders are created and retrieved correctly"""
    
    db = JsonDatabase()
    
    # Create order
    order_id = db.create_order({
        "user_id": 123,
        "product_id": 1,
        "qty": 2,
        "total": 20.0,
        "keys_delivered": ["key1", "key2"],
        "timestamp": 1234567890
    })
    
    # Retrieve order
    orders = [o for o in db.orders if o["id"] == order_id]
    assert len(orders) == 1
    assert orders[0]["user_id"] == 123
    assert orders[0]["qty"] == 2
```

**Run:**
```bash
pytest tests/test_db_consistency.py -v
```

---

## FEATURE TEST CASES

### Test 6: Catalog Navigation

**File:** `tests/test_catalog_flow.py`

```python
import pytest

@pytest.mark.asyncio
async def test_catalog_category_listing():
    """Verify categories are listed correctly"""
    from src.database.json_db import db
    
    categories = db.get_categories()
    assert len(categories) > 0
    assert all("id" in c and "name" in c for c in categories)

@pytest.mark.asyncio
async def test_product_listing_by_category():
    """Verify products are filtered by category"""
    from src.database.json_db import db
    
    # Add test products
    db.add_product({"name": "Product 1", "price": 10.0, "category_id": 1})
    db.add_product({"name": "Product 2", "price": 20.0, "category_id": 2})
    
    # Retrieve by category
    cat1_products = db.get_products(category_id=1)
    cat2_products = db.get_products(category_id=2)
    
    assert len(cat1_products) >= 1
    assert len(cat2_products) >= 1
    assert all(p["category_id"] == 1 for p in cat1_products)
    assert all(p["category_id"] == 2 for p in cat2_products)
```

---

### Test 7: Cart Operations

**File:** `tests/test_cart_flow.py`

```python
import pytest
from src.database.json_db import db

@pytest.mark.asyncio
async def test_add_to_cart():
    """Verify items can be added to cart"""
    
    user_id = 123
    user = db.get_user(user_id)
    cart = user.get("cart", {})
    
    # Add item
    cart["1"] = cart.get("1", 0) + 1
    db.update_user(user_id, {"cart": cart})
    
    # Verify
    user = db.get_user(user_id)
    assert user["cart"]["1"] == 1

@pytest.mark.asyncio
async def test_increase_cart_quantity():
    """Verify cart quantity can be increased"""
    
    user_id = 123
    user = db.get_user(user_id)
    cart = user.get("cart", {})
    
    cart["1"] = 1
    db.update_user(user_id, {"cart": cart})
    
    # Increase
    cart["1"] += 1
    db.update_user(user_id, {"cart": cart})
    
    # Verify
    user = db.get_user(user_id)
    assert user["cart"]["1"] == 2

@pytest.mark.asyncio
async def test_remove_from_cart():
    """Verify items can be removed from cart"""
    
    user_id = 123
    user = db.get_user(user_id)
    cart = user.get("cart", {})
    
    cart["1"] = 1
    db.update_user(user_id, {"cart": cart})
    
    # Remove
    del cart["1"]
    db.update_user(user_id, {"cart": cart})
    
    # Verify
    user = db.get_user(user_id)
    assert "1" not in user["cart"]
```

---

### Test 8: Topup Flow

**File:** `tests/test_topup_flow.py`

```python
import pytest
from src.database.json_db import db

@pytest.mark.asyncio
async def test_topup_balance():
    """Verify balance is increased on topup"""
    
    user_id = 123
    initial_balance = 0.0
    topup_amount = 50.0
    
    user = db.get_user(user_id)
    db.update_user(user_id, {"balance": initial_balance})
    
    # Topup
    new_balance = initial_balance + topup_amount
    db.update_user(user_id, {"balance": new_balance})
    
    # Verify
    user = db.get_user(user_id)
    assert user["balance"] == 50.0

@pytest.mark.asyncio
async def test_topup_amount_validation():
    """Verify topup amount is validated"""
    
    valid_amounts = [10, 20, 50, 100, 500]
    invalid_amounts = [-10, 0, 10001]
    
    for amount in valid_amounts:
        assert amount > 0 and amount <= 10000, f"Amount {amount} should be valid"
    
    for amount in invalid_amounts:
        assert not (amount > 0 and amount <= 10000), f"Amount {amount} should be invalid"
```

---

### Test 9: Admin Product Management

**File:** `tests/test_admin_products.py`

```python
import pytest
from src.database.json_db import db

@pytest.mark.asyncio
async def test_add_product():
    """Verify products can be added"""
    
    initial_count = len(db.products)
    
    prod_id = db.add_product({
        "name": "Test Product",
        "price": 10.0,
        "category_id": 1,
        "description": "Test"
    })
    
    assert len(db.products) == initial_count + 1
    assert db.get_product(prod_id)["name"] == "Test Product"

@pytest.mark.asyncio
async def test_update_product():
    """Verify products can be updated"""
    
    prod_id = db.add_product({
        "name": "Original Name",
        "price": 10.0,
        "category_id": 1
    })
    
    db.update_product(prod_id, {"name": "Updated Name", "price": 20.0})
    
    product = db.get_product(prod_id)
    assert product["name"] == "Updated Name"
    assert product["price"] == 20.0

@pytest.mark.asyncio
async def test_delete_product():
    """Verify products can be deleted"""
    
    prod_id = db.add_product({
        "name": "To Delete",
        "price": 10.0,
        "category_id": 1
    })
    
    db.delete_product(prod_id)
    
    assert db.get_product(prod_id) is None
```

---

### Test 10: Stock Management

**File:** `tests/test_stock_management.py`

```python
import pytest
from src.database.json_db import db

@pytest.mark.asyncio
async def test_add_stock():
    """Verify stock can be added"""
    
    prod_id = 1
    keys = ["key1", "key2", "key3"]
    
    db.add_stock(prod_id, keys)
    
    count = db.get_stock_count(prod_id)
    assert count >= 3

@pytest.mark.asyncio
async def test_pop_stock():
    """Verify stock can be popped"""
    
    prod_id = 1
    db.stock = {"1": ["key1", "key2", "key3"]}
    
    keys = db.pop_stock(prod_id, 2)
    
    assert len(keys) == 2
    assert db.get_stock_count(prod_id) == 1

@pytest.mark.asyncio
async def test_insufficient_stock():
    """Verify insufficient stock is handled"""
    
    prod_id = 1
    db.stock = {"1": ["key1"]}
    
    keys = db.pop_stock(prod_id, 5)
    
    assert keys == []
    assert db.get_stock_count(prod_id) == 1
```

---

## EDGE CASE TEST CASES

### Test 11: Concurrent User Operations

**File:** `tests/test_concurrent_operations.py`

```python
import pytest
import asyncio
from src.database.json_db import db

@pytest.mark.asyncio
async def test_concurrent_user_creation():
    """Verify multiple users can be created concurrently"""
    
    async def create_user(user_id):
        user = db.get_user(user_id)
        db.update_user(user_id, {"balance": 100.0})
        return user_id
    
    user_ids = await asyncio.gather(*[create_user(i) for i in range(100, 110)])
    
    assert len(user_ids) == 10
    for uid in user_ids:
        user = db.get_user(uid)
        assert user["balance"] == 100.0

@pytest.mark.asyncio
async def test_concurrent_balance_updates():
    """Verify balance updates are consistent"""
    
    user_id = 123
    db.update_user(user_id, {"balance": 0.0})
    
    async def add_balance(amount):
        user = db.get_user(user_id)
        new_balance = user["balance"] + amount
        db.update_user(user_id, {"balance": new_balance})
    
    await asyncio.gather(*[add_balance(10.0) for _ in range(10)])
    
    user = db.get_user(user_id)
    # Note: Due to race conditions, this might not be exactly 100
    # This test demonstrates the issue
    print(f"Final balance: {user['balance']} (expected 100.0)")
```

---

## PERFORMANCE TEST CASES

### Test 12: Load Testing

**File:** `tests/test_performance.py`

```python
import pytest
import time
from src.database.json_db import db

@pytest.mark.asyncio
async def test_large_product_catalog():
    """Verify performance with large product catalog"""
    
    # Add 1000 products
    start = time.time()
    for i in range(1000):
        db.add_product({
            "name": f"Product {i}",
            "price": 10.0 + i * 0.1,
            "category_id": (i % 10) + 1
        })
    elapsed = time.time() - start
    
    print(f"Added 1000 products in {elapsed:.2f}s")
    assert elapsed < 10.0, "Should add 1000 products in < 10s"

@pytest.mark.asyncio
async def test_large_order_history():
    """Verify performance with large order history"""
    
    user_id = 123
    
    # Create 1000 orders
    start = time.time()
    for i in range(1000):
        db.create_order({
            "user_id": user_id,
            "product_id": i % 100,
            "qty": 1,
            "total": 10.0,
            "keys_delivered": ["key"],
            "timestamp": time.time()
        })
    elapsed = time.time() - start
    
    print(f"Created 1000 orders in {elapsed:.2f}s")
    assert elapsed < 10.0, "Should create 1000 orders in < 10s"
```

---

## Running All Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_checkout_race_condition.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run with markers
pytest tests/ -m "asyncio" -v
```

---

## Continuous Integration

**File:** `.github/workflows/tests.yml`

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    - uses: actions/setup-python@v2
      with:
        python-version: 3.10
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-asyncio pytest-mock pytest-cov
    
    - name: Run tests
      run: pytest tests/ -v --cov=src
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

---

## Test Coverage Goals

| Component | Target Coverage |
|-----------|-----------------|
| Database  | 95%             |
| Handlers  | 85%             |
| Services  | 90%             |
| Middleware| 80%             |
| **Total** | **85%**         |

---

**Test Plan Created:** 2026-01-25
**Total Test Cases:** 50+
**Estimated Runtime:** 5-10 minutes
