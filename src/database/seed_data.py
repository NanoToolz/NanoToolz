import random
import string
from src.database import db


def generate_key():
    parts = [''.join(random.choices(string.ascii_uppercase + string.digits, k=4)) for _ in range(4)]
    return '-'.join(parts)


def generate_email_pass():
    domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'mail.com', 'proton.me']
    names = ['user', 'john', 'jane', 'mike', 'sarah', 'alex', 'emma', 'david', 'lisa', 'chris']
    name = random.choice(names)
    num = random.randint(100, 9999)
    domain = random.choice(domains)
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(8, 12)))
    return f"{name}{num}@{domain}:{password}"


def generate_link(base_url):
    code = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
    return f"{base_url}/{code}"


def generate_gift_card_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))


DEMO_DATA = {
    "Streaming Accounts": {
        "emoji": "🎬",
        "products": [
            {"name": "Netflix Premium 4K", "price": 4.99, "type": "credentials", "desc": "Netflix Premium with 4K UHD streaming. 1 month warranty.", "count": 50},
            {"name": "Spotify Premium", "price": 2.99, "type": "credentials", "desc": "Spotify Premium account with ad-free music. Lifetime warranty.", "count": 50},
            {"name": "Disney+ Premium", "price": 3.99, "type": "credentials", "desc": "Disney+ Premium with all content access. 1 month warranty.", "count": 30},
            {"name": "HBO Max", "price": 4.49, "type": "credentials", "desc": "HBO Max premium account. Full access to all shows.", "count": 25},
            {"name": "Hulu Premium", "price": 3.49, "type": "credentials", "desc": "Hulu Premium no ads. Includes Live TV.", "count": 30},
        ]
    },
    "Gaming": {
        "emoji": "🎮",
        "products": [
            {"name": "Steam Random Key", "price": 1.99, "type": "key", "desc": "Random Steam game key. Minimum $10 value guaranteed.", "count": 40},
            {"name": "Xbox Game Pass Ultimate", "price": 8.99, "type": "key", "desc": "Xbox Game Pass Ultimate 1 month code.", "count": 30},
            {"name": "PlayStation Plus Essential", "price": 6.99, "type": "key", "desc": "PlayStation Plus Essential 1 month code.", "count": 25},
            {"name": "Nintendo eShop $10", "price": 8.99, "type": "key", "desc": "Nintendo eShop gift card code.", "count": 20},
            {"name": "EA Play Pro", "price": 5.99, "type": "key", "desc": "EA Play Pro 1 month subscription key.", "count": 25},
        ]
    },
    "VPN Services": {
        "emoji": "🔒",
        "products": [
            {"name": "NordVPN Premium", "price": 3.99, "type": "credentials", "desc": "NordVPN premium account. 1 year subscription.", "count": 40},
            {"name": "ExpressVPN Premium", "price": 4.49, "type": "credentials", "desc": "ExpressVPN premium account. Fast servers worldwide.", "count": 30},
            {"name": "Surfshark VPN", "price": 2.99, "type": "credentials", "desc": "Surfshark VPN unlimited devices. Great value.", "count": 35},
            {"name": "CyberGhost VPN", "price": 2.49, "type": "credentials", "desc": "CyberGhost VPN premium. 7000+ servers.", "count": 30},
        ]
    },
    "Software Keys": {
        "emoji": "💻",
        "products": [
            {"name": "Windows 11 Pro Key", "price": 12.99, "type": "key", "desc": "Windows 11 Pro retail license key. Lifetime activation.", "count": 20},
            {"name": "Office 365 Key", "price": 9.99, "type": "key", "desc": "Microsoft Office 365 1 year subscription key.", "count": 25},
            {"name": "Adobe Creative Cloud", "price": 15.99, "type": "credentials", "desc": "Adobe Creative Cloud account. All apps included.", "count": 15},
            {"name": "Windows 10 Pro Key", "price": 8.99, "type": "key", "desc": "Windows 10 Pro retail license key. Lifetime activation.", "count": 25},
            {"name": "Malwarebytes Premium", "price": 4.99, "type": "key", "desc": "Malwarebytes Premium 1 year license.", "count": 20},
        ]
    },
    "Premium Links": {
        "emoji": "🔗",
        "products": [
            {"name": "Mega.nz Premium Link", "price": 0.99, "type": "link", "desc": "Mega.nz premium download link. Fast speeds.", "count": 50},
            {"name": "Rapidgator Premium", "price": 0.89, "type": "link", "desc": "Rapidgator premium download link.", "count": 40},
            {"name": "Uploaded Premium", "price": 0.79, "type": "link", "desc": "Uploaded.net premium download link.", "count": 35},
        ]
    },
    "Gift Cards": {
        "emoji": "🎁",
        "products": [
            {"name": "Amazon Gift Card $10", "price": 9.49, "type": "key", "desc": "Amazon gift card $10 value. US region.", "count": 20},
            {"name": "Google Play $5", "price": 4.49, "type": "key", "desc": "Google Play gift card $5 value. US region.", "count": 30},
            {"name": "iTunes $10", "price": 8.99, "type": "key", "desc": "iTunes/Apple gift card $10 value. US region.", "count": 25},
            {"name": "Steam Wallet $20", "price": 18.99, "type": "key", "desc": "Steam wallet gift card $20 value.", "count": 15},
            {"name": "PlayStation Store $10", "price": 9.49, "type": "key", "desc": "PlayStation Store gift card $10 value. US region.", "count": 20},
        ]
    },
}


def generate_stock_item(product_type: str, product_name: str) -> str:
    if product_type == "credentials":
        return generate_email_pass()
    elif product_type == "link":
        if "mega" in product_name.lower():
            return generate_link("https://mega.nz/file")
        elif "rapidgator" in product_name.lower():
            return generate_link("https://rapidgator.net/file")
        else:
            return generate_link("https://uploaded.net/file")
    else:
        return generate_key()


def seed_database():
    existing_categories = db.get_categories()
    if existing_categories:
        return False

    for cat_name, cat_data in DEMO_DATA.items():
        category = db.create_category(
            name=cat_name,
            emoji=cat_data["emoji"],
            description=f"{cat_name} - Digital products"
        )

        if not category:
            continue

        cat_id = category["id"]

        for prod in cat_data["products"]:
            product = db.create_product(
                category_id=cat_id,
                name=prod["name"],
                price=prod["price"],
                description=prod["desc"],
                product_type=prod["type"]
            )

            if not product:
                continue

            stock_items = []
            for _ in range(prod["count"]):
                item = generate_stock_item(prod["type"], prod["name"])
                stock_items.append(item)

            if stock_items:
                db.add_stock(product["id"], stock_items)

    db.create_coupon("WELCOME10", discount_percent=10, max_uses=100)
    db.create_coupon("SAVE20", discount_percent=20, max_uses=50)
    db.create_coupon("VIP50", discount_percent=50, max_uses=10)

    return True
