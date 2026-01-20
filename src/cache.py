"""Cache and state management"""

# Simple in-memory cache for user data
user_cache = {}
cart_data = {}
payment_pending = {}

def get_user_cart(user_id: int):
    """Get user's shopping cart"""
    if user_id not in cart_data:
        cart_data[user_id] = []
    return cart_data[user_id]

def add_to_cart(user_id: int, product_id: int, quantity: int = 1):
    """Add product to cart"""
    cart = get_user_cart(user_id)
    
    # Check if product already in cart
    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            return
    
    cart.append({"product_id": product_id, "quantity": quantity})

def clear_cart(user_id: int):
    """Clear user's cart"""
    if user_id in cart_data:
        cart_data[user_id] = []

def get_cart_total(user_id: int, db) -> tuple[float, float]:
    """Calculate cart total in USD and USDT"""
    from src.database.models import Product
    cart = get_user_cart(user_id)
    
    total_usd = 0
    total_usdt = 0
    
    for item in cart:
        product = db.query(Product).filter(Product.id == item["product_id"]).first()
        if product:
            total_usd += float(product.price_usd) * item["quantity"]
            total_usdt += float(product.price_usdt) * item["quantity"]
    
    return total_usd, total_usdt
