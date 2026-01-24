from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, DECIMAL, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    language = Column(String, default="en")
    currency = Column(String, default="USD")
    credits = Column(DECIMAL(10, 2), default=0)
    referral_code = Column(String, unique=True, index=True)
    referred_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_banned = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    orders = relationship("Order", back_populates="user")
    support_tickets = relationship("SupportTicket", back_populates="user")
    cart_items = relationship("CartItem", back_populates="user", cascade="all, delete-orphan")
    wishlist_items = relationship("WishlistItem", back_populates="user", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text, nullable=True)
    emoji = Column(String, default="📦")
    display_order = Column(Integer, default=0)
    featured = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    products = relationship("Product", back_populates="category")

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    name = Column(String, index=True)
    description = Column(Text)
    price_usd = Column(DECIMAL(10, 2))
    price_usdt = Column(DECIMAL(10, 2))
    price_initial_usd = Column(DECIMAL(10, 2), nullable=False, default=0)
    price_initial_usdt = Column(DECIMAL(10, 2), nullable=False, default=0)
    price_drop_per_day_usd = Column(DECIMAL(10, 4), default=0)
    price_drop_per_day_usdt = Column(DECIMAL(10, 4), default=0)
    price_minimum_usd = Column(DECIMAL(10, 2), nullable=False, default=0)
    price_minimum_usdt = Column(DECIMAL(10, 2), nullable=False, default=0)
    drop_period_days = Column(Integer, default=30)
    price_last_calculated = Column(DateTime, default=datetime.utcnow)
    product_type = Column(String)  # key, file, license, subscription, course
    stock = Column(Integer, nullable=True)  # NULL = unlimited
    sales_count = Column(Integer, default=0)
    rating = Column(Float, default=0)
    review_count = Column(Integer, default=0)
    image_url = Column(String, nullable=True)
    status = Column(String, default="published")  # draft, published, archived
    affiliate_commission = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    category = relationship("Category", back_populates="products")
    deliveries = relationship("ProductDelivery", back_populates="product")
    orders = relationship("Order", back_populates="product")
    reviews = relationship("Review", back_populates="product", cascade="all, delete-orphan")
    wishlist_items = relationship("WishlistItem", back_populates="product", cascade="all, delete-orphan")

class ProductDelivery(Base):
    __tablename__ = "product_deliveries"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    delivery_content = Column(Text)  # keys, file URL, access link
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    product = relationship("Product", back_populates="deliveries")

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, default=1)
    price_paid_usd = Column(DECIMAL(10, 2))
    price_paid_usdt = Column(DECIMAL(10, 2))
    credits_used = Column(DECIMAL(10, 2), default=0)
    payment_method = Column(String)  # usdt_tron, usdt_eth, credits
    payment_ref = Column(String, index=True, nullable=True)
    payment_status = Column(String, default="pending")  # pending, completed, failed
    delivery_status = Column(String, default="pending")  # pending, sent, failed
    tx_hash = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="orders")
    product = relationship("Product", back_populates="orders")

class Referral(Base):
    __tablename__ = "referrals"
    
    id = Column(Integer, primary_key=True, index=True)
    referrer_id = Column(Integer, ForeignKey("users.id"))
    referred_user_id = Column(Integer, ForeignKey("users.id"))
    earnings = Column(DECIMAL(10, 2), default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class DailySpin(Base):
    __tablename__ = "daily_spins"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    reward_type = Column(String)  # credits, coupon, discount
    reward_value = Column(DECIMAL(10, 2))
    spin_date = Column(DateTime, default=datetime.utcnow)

class SupportTicket(Base):
    __tablename__ = "support_tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    category = Column(String)  # general, order_issue, account, bug, feature
    subject = Column(String)
    message = Column(Text)
    status = Column(String, default="open")  # open, in_progress, resolved
    priority = Column(String, default="normal")  # low, normal, high
    assigned_to = Column(String, nullable=True)
    responses = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="support_tickets")

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    payment_ref = Column(String, index=True)
    amount = Column(DECIMAL(10, 2))
    currency = Column(String, default="USDT")
    method = Column(String)  # usdt_tron, ltc
    tx_hash = Column(String, unique=True, index=True)
    wallet_from = Column(String)
    wallet_to = Column(String)
    status = Column(String, default="pending")  # pending, confirmed, failed
    confirmations = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="cart_items")
    product = relationship("Product")


class WishlistItem(Base):
    __tablename__ = "wishlist_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="wishlist_items")
    product = relationship("Product", back_populates="wishlist_items")


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    rating = Column(Integer, default=5)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="reviews")
    product = relationship("Product", back_populates="reviews")


class Setting(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    value = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Coupon(Base):
    __tablename__ = "coupons"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    discount_type = Column(String, default="percent")  # percent, fixed
    value = Column(DECIMAL(10, 2), default=0)
    usage_limit = Column(Integer, default=0)
    used_count = Column(Integer, default=0)
    active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
