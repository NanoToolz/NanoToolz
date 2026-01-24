"""
Seed dummy data for testing
"""
from sqlalchemy.orm import Session
from src.database import SessionLocal
from src.database.models import Category, Product, User
from src.logger import logger

def seed_dummy_data():
    """Seed initial categories and products"""
    db: Session = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(Category).count() > 0:
            logger.info("Database already seeded, skipping...")
            return
        
        # Create categories
        categories = [
            Category(name="Software", emoji="💻", display_order=1),
            Category(name="E-Books", emoji="📚", display_order=2),
            Category(name="Courses", emoji="🎓", display_order=3),
            Category(name="Templates", emoji="📋", display_order=4),
        ]
        
        for cat in categories:
            db.add(cat)
        db.commit()
        logger.info("✅ Categories seeded")
        
        # Create sample products
        products = [
            Product(
                category_id=1,
                name="Premium WordPress Theme",
                description="Professional WordPress theme with drag-and-drop builder",
                price_usd=49.99,
                price_usdt=49.99,
                product_type="software",
                stock=None,
                status="published"
            ),
            Product(
                category_id=1,
                name="Python Course Bundle",
                description="Complete Python programming course from beginner to advanced",
                price_usd=29.99,
                price_usdt=29.99,
                product_type="course",
                stock=None,
                status="published"
            ),
            Product(
                category_id=2,
                name="Digital Marketing Guide",
                description="Complete guide to modern digital marketing strategies",
                price_usd=14.99,
                price_usdt=14.99,
                product_type="ebook",
                stock=None,
                status="published"
            ),
            Product(
                category_id=3,
                name="Web Development Masterclass",
                description="Learn HTML, CSS, JavaScript, and React from experts",
                price_usd=79.99,
                price_usdt=79.99,
                product_type="course",
                stock=None,
                status="published"
            ),
            Product(
                category_id=4,
                name="Landing Page Templates",
                description="50+ high-converting landing page templates",
                price_usd=39.99,
                price_usdt=39.99,
                product_type="template",
                stock=None,
                status="published"
            ),
            Product(
                category_id=2,
                name="AI Prompt Engineering",
                description="Master the art of prompting AI models for maximum output",
                price_usd=24.99,
                price_usdt=24.99,
                product_type="ebook",
                stock=None,
                status="published"
            ),
        ]
        
        for prod in products:
            db.add(prod)
        db.commit()
        logger.info("✅ Products seeded")

        # Add sample stock/delivery items
        from src.database.models import ProductDelivery
        stock_items = [
            ProductDelivery(product_id=1, delivery_content="KEY-ABC123-XYZ789"),
            ProductDelivery(product_id=1, delivery_content="KEY-DEF456-UVW000"),
            ProductDelivery(product_id=2, delivery_content="https://example.com/python-course-access"),
            ProductDelivery(product_id=3, delivery_content="Download: https://example.com/marketing-guide.pdf"),
            ProductDelivery(product_id=4, delivery_content="Invite: https://t.me/+PrivateCourseLink"),
        ]
        for item in stock_items:
            db.add(item)
        db.commit()
        logger.info("✅ Stock items seeded")
        
        # Create a test admin user with credits
        admin = User(
            telegram_id=123456789,
            username="admin",
            first_name="Admin",
            credits=1000.00
        )
        db.add(admin)
        db.commit()
        logger.info("✅ Seed data complete!")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Seed error: {e}")
    finally:
        db.close()