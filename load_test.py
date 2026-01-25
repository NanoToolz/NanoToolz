import asyncio
import random
from unittest.mock import MagicMock
from src.database import json_db
from src.bot.features.cart.handlers import add_to_cart
from src.bot.features.checkout.handlers import start_checkout, process_payment_credits

# Initialize test database
json_db.reset_db()

# Create test products
for i in range(1, 6):
    json_db.add_product({
        "id": i,
        "name": f"Product {i}",
        "price": 10.0,
        "stock_count": 100,
        "keys": [f"KEY-{i}-{j}" for j in range(100)]
    })

# Create test users
for i in range(1, 101):
    json_db.add_user({
        "id": i,
        "telegram_id": i,
        "balance": 1000.0,
        "cart": {}
    })

async def simulate_user(user_id):
    """Simulate a user completing checkout"""
    # Create mock callback objects
    callback = MagicMock()
    callback.from_user.id = user_id
    callback.message = MagicMock()
    callback.message.edit_text = MagicMock()
    callback.answer = MagicMock()
    
    # Add random product to cart
    product_id = random.randint(1, 5)
    callback.data = f"add_cart_{product_id}"
    await add_to_cart(callback)
    
    # Start checkout
    callback.data = "checkout_start"
    await start_checkout(callback)
    
    # Process payment
    callback.data = "pay_credits"
    await process_payment_credits(callback)
    
    return True

async def main():
    """Run concurrent load test"""
    tasks = [simulate_user(i) for i in range(1, 101)]
    await asyncio.gather(*tasks)
    
    # Verify stock integrity
    for i in range(1, 6):
        product = json_db.get_product(i)
        stock = json_db.get_stock_count(i)
        sales = sum(1 for o in json_db.orders if o['product_id'] == i)
        remaining_stock = 100 - sales
        
        assert stock == remaining_stock, \
            f"Product {i} stock mismatch: {stock} vs expected {remaining_stock}"
    
    print("✅ All stock checks passed!")

if __name__ == "__main__":
    asyncio.run(main())