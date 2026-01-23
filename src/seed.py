import uuid
from sqlalchemy.orm import Session
from src.database.models import Category, Product, ProductDelivery, Setting
from src.database import SessionLocal


DEFAULT_SETTINGS = {
    "store_name": "NanoToolz Store",
    "support_contact": "@YourSupport",
    "payment_usdt_tron_wallet": "TXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    "payment_ltc_wallet": "LXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    "payment_notice": "Send the exact amount and tap 'I Paid' after payment.",
}


def seed_settings(db: Session) -> None:
    for key, value in DEFAULT_SETTINGS.items():
        existing = db.query(Setting).filter(Setting.key == key).first()
        if not existing:
            db.add(Setting(key=key, value=value))
    db.commit()

def seed_dummy_data():
    """Seed database with dummy products and categories"""
    db = SessionLocal()
    seed_settings(db)
    if db.query(Category).first():
        db.close()
        print("ℹ️  Data already present, skipping seed.")
        return
    
    # Create categories
    categories_data = [
        {"name": "Programming Courses", "emoji": "🎓", "featured": True},
        {"name": "License Keys", "emoji": "🔑", "featured": True},
        {"name": "Tools & Software", "emoji": "⚙️", "featured": True},
        {"name": "Templates & Assets", "emoji": "🎨", "featured": True},
        {"name": "E-Books", "emoji": "📚", "featured": True},
    ]
    
    categories = {}
    for i, cat_data in enumerate(categories_data):
        cat = Category(
            name=cat_data["name"],
            emoji=cat_data["emoji"],
            featured=cat_data["featured"],
            display_order=i
        )
        db.add(cat)
        db.flush()
        categories[cat_data["name"]] = cat
    
    db.commit()
    
    # Create products
    products_data = [
        # Programming Courses
        {
            "name": "Complete Python 101 Masterclass",
            "category": "Programming Courses",
            "description": "Learn Python from scratch to advanced. Includes 50+ hours of video tutorials, quizzes, and real-world projects.",
            "price_usd": 99.99,
            "price_usdt": 99.50,
            "product_type": "course",
            "stock": None,
            "rating": 4.8,
            "review_count": 234,
            "sales_count": 1250,
            "affiliate_commission": 15
        },
        {
            "name": "Telegram Bot Development with Aiogram v3",
            "category": "Programming Courses",
            "description": "Master Telegram bot development using aiogram v3. Build production-ready bots with payments, databases, and AI integration.",
            "price_usd": 79.99,
            "price_usdt": 79.50,
            "product_type": "course",
            "stock": None,
            "rating": 4.9,
            "review_count": 189,
            "sales_count": 856,
            "affiliate_commission": 15
        },
        {
            "name": "Web Development Bootcamp 2024",
            "category": "Programming Courses",
            "description": "Full-stack web development course. HTML, CSS, JavaScript, React, Node.js, MongoDB, and deployment.",
            "price_usd": 149.99,
            "price_usdt": 149.50,
            "product_type": "course",
            "stock": None,
            "rating": 4.7,
            "review_count": 412,
            "sales_count": 2103,
            "affiliate_commission": 15
        },
        
        # License Keys
        {
            "name": "Windows 10 Pro License Key",
            "category": "License Keys",
            "description": "Genuine Windows 10 Professional license key. Instant activation, lifetime support.",
            "price_usd": 29.99,
            "price_usdt": 29.50,
            "product_type": "key",
            "stock": 50,
            "rating": 4.6,
            "review_count": 567,
            "sales_count": 3421,
            "affiliate_commission": 10
        },
        {
            "name": "Microsoft Office 2024 Professional",
            "category": "License Keys",
            "description": "MS Office 2024 with Word, Excel, PowerPoint, Outlook. Licensed for 1 PC.",
            "price_usd": 59.99,
            "price_usdt": 59.50,
            "product_type": "key",
            "stock": 100,
            "rating": 4.8,
            "review_count": 892,
            "sales_count": 5234,
            "affiliate_commission": 10
        },
        {
            "name": "Adobe Creative Cloud 1-Year Subscription",
            "category": "License Keys",
            "description": "Unlimited access to all Adobe apps (Photoshop, Premiere Pro, After Effects, etc)",
            "price_usd": 54.99,
            "price_usdt": 54.50,
            "product_type": "subscription",
            "stock": None,
            "rating": 4.9,
            "review_count": 1243,
            "sales_count": 4156,
            "affiliate_commission": 12
        },
        
        # Tools & Software
        {
            "name": "Video Editing Suite Pro",
            "category": "Tools & Software",
            "description": "Professional video editing tool. Supports 4K, effects, color grading, and rendering.",
            "price_usd": 149.99,
            "price_usdt": 149.50,
            "product_type": "file",
            "stock": None,
            "rating": 4.5,
            "review_count": 342,
            "sales_count": 1876,
            "affiliate_commission": 20
        },
        {
            "name": "SEO & Marketing Automation Tool",
            "category": "Tools & Software",
            "description": "All-in-one SEO tool. Keyword research, backlink analysis, competitor tracking, rank monitoring.",
            "price_usd": 99.99,
            "price_usdt": 99.50,
            "product_type": "license",
            "stock": None,
            "rating": 4.7,
            "review_count": 678,
            "sales_count": 2341,
            "affiliate_commission": 18
        },
        {
            "name": "Photo Editing & Design Software",
            "category": "Tools & Software",
            "description": "Professional photo editor with 500+ filters, effects, and design tools.",
            "price_usd": 49.99,
            "price_usdt": 49.50,
            "product_type": "file",
            "stock": None,
            "rating": 4.4,
            "review_count": 521,
            "sales_count": 1543,
            "affiliate_commission": 15
        },
        
        # Templates & Assets
        {
            "name": "50 Premium Figma UI Kits",
            "category": "Templates & Assets",
            "description": "Complete Figma UI kits. 50 designs ready to customize for your projects.",
            "price_usd": 39.99,
            "price_usdt": 39.50,
            "product_type": "file",
            "stock": None,
            "rating": 4.6,
            "review_count": 234,
            "sales_count": 892,
            "affiliate_commission": 20
        },
        {
            "name": "1000+ Icon Pack for Web & Mobile",
            "category": "Templates & Assets",
            "description": "Comprehensive icon set. SVG, PNG, Web fonts. Ready for any project.",
            "price_usd": 19.99,
            "price_usdt": 19.50,
            "product_type": "file",
            "stock": None,
            "rating": 4.8,
            "review_count": 445,
            "sales_count": 2156,
            "affiliate_commission": 25
        },
        {
            "name": "Website Template Bundle (30 Templates)",
            "category": "Templates & Assets",
            "description": "30 modern, responsive website templates. HTML, CSS, JavaScript included.",
            "price_usd": 49.99,
            "price_usdt": 49.50,
            "product_type": "file",
            "stock": None,
            "rating": 4.7,
            "review_count": 312,
            "sales_count": 1534,
            "affiliate_commission": 20
        },
        
        # E-Books
        {
            "name": "The Complete Digital Marketing Handbook",
            "category": "E-Books",
            "description": "Comprehensive guide to digital marketing. SEO, SEM, Social Media, Email, Analytics.",
            "price_usd": 29.99,
            "price_usdt": 29.50,
            "product_type": "file",
            "stock": None,
            "rating": 4.6,
            "review_count": 178,
            "sales_count": 654,
            "affiliate_commission": 25
        },
        {
            "name": "Cryptocurrency Investing Guide 2024",
            "category": "E-Books",
            "description": "Bitcoin, Ethereum, DeFi explained. Investment strategies for beginners to advanced.",
            "price_usd": 24.99,
            "price_usdt": 24.50,
            "product_type": "file",
            "stock": None,
            "rating": 4.5,
            "review_count": 234,
            "sales_count": 876,
            "affiliate_commission": 25
        },
        {
            "name": "Freelancing Mastery - From Zero to $10K/Month",
            "category": "E-Books",
            "description": "Complete guide to freelancing. Finding clients, pricing, scaling your business.",
            "price_usd": 34.99,
            "price_usdt": 34.50,
            "product_type": "file",
            "stock": None,
            "rating": 4.9,
            "review_count": 567,
            "sales_count": 1432,
            "affiliate_commission": 25
        },
    ]
    
    for prod_data in products_data:
        category = categories[prod_data.pop("category")]
        
        product = Product(
            category_id=category.id,
            **prod_data
        )
        db.add(product)
        db.flush()
        
        # Add dummy delivery content
        if product.product_type == "key":
            delivery = ProductDelivery(
                product_id=product.id,
                delivery_content=f"KEY-{uuid.uuid4().hex[:12].upper()}"
            )
            db.add(delivery)
        elif product.product_type in ["file", "course"]:
            delivery = ProductDelivery(
                product_id=product.id,
                delivery_content=f"https://download.example.com/{product.id}/product.zip"
            )
            db.add(delivery)
        elif product.product_type == "license":
            delivery = ProductDelivery(
                product_id=product.id,
                delivery_content=f"License will be emailed to your registered email. Access link: https://license.example.com/activate/{uuid.uuid4().hex}"
            )
            db.add(delivery)
        elif product.product_type == "subscription":
            delivery = ProductDelivery(
                product_id=product.id,
                delivery_content=f"Subscription activated. Dashboard: https://dashboard.example.com/user/{uuid.uuid4().hex}"
            )
            db.add(delivery)
    
    db.commit()
    db.close()
    print("✅ Dummy data seeded successfully!")

if __name__ == "__main__":
    seed_dummy_data()
