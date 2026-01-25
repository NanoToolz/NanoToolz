from __future__ import annotations

from datetime import datetime

from src.database.models import Product

DEFAULT_USDT_RATE = 0.99


async def get_usdt_rate() -> float:
    """Get current USDT to USD rate from CoinGecko API."""
    import aiohttp

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.coingecko.com/api/v3/simple/price?ids=tether&vs_currencies=usd",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as resp:
                data = await resp.json()
                return float(data["tether"]["usd"])
    except Exception:
        return 1.0


def calculate_current_price(product: Product, currency: str = "USD") -> float:
    days_elapsed = max(0, (datetime.utcnow().date() - product.created_at.date()).days)

    if currency.upper() == "USDT":
        initial = float(product.price_initial_usdt or product.price_usdt or 0)
        daily_drop = float(product.price_drop_per_day_usdt or 0)
        minimum = float(product.price_minimum_usdt or 0)
    else:
        initial = float(product.price_initial_usd or product.price_usd or 0)
        daily_drop = float(product.price_drop_per_day_usd or 0)
        minimum = float(product.price_minimum_usd or 0)

    current = initial - (daily_drop * days_elapsed)
    return round(max(current, minimum), 2)


def get_price_display_info(product: Product) -> dict:
    days_elapsed = max(0, (datetime.utcnow().date() - product.created_at.date()).days)

    initial_usd = float(product.price_initial_usd or product.price_usd or 0)
    initial_usdt = float(product.price_initial_usdt or product.price_usdt or 0)
    minimum_usd = float(product.price_minimum_usd or 0)
    minimum_usdt = float(product.price_minimum_usdt or 0)
    daily_drop_usd = float(product.price_drop_per_day_usd or 0)

    current_usd = calculate_current_price(product, "USD")
    current_usdt = calculate_current_price(product, "USDT")

    if daily_drop_usd > 0:
        total_days = int(max((initial_usd - minimum_usd) / daily_drop_usd, 0))
        days_until_minimum = max(total_days - days_elapsed, 0)
    else:
        days_until_minimum = 0

    if initial_usd > 0:
        discount_percentage = max(((initial_usd - current_usd) / initial_usd) * 100, 0)
    else:
        discount_percentage = 0

    if current_usd <= minimum_usd and minimum_usd > 0:
        status = "at_minimum"
    elif days_elapsed == 0:
        status = "new"
    else:
        status = "dropping"

    return {
        "current_price_usd": round(current_usd, 2),
        "current_price_usdt": round(current_usdt, 2),
        "initial_price_usd": round(initial_usd, 2),
        "initial_price_usdt": round(initial_usdt, 2),
        "minimum_price_usd": round(minimum_usd, 2),
        "minimum_price_usdt": round(minimum_usdt, 2),
        "days_elapsed": days_elapsed,
        "days_until_minimum": days_until_minimum,
        "daily_drop_usd": round(daily_drop_usd, 3),
        "discount_percentage": round(discount_percentage, 2),
        "status": status,
    }


def set_product_pricing(
    db,
    product_id: int,
    initial_price_usd: float,
    drop_period_days: int,
    minimum_price_usd: float,
) -> None:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return

    drop_period_days = max(int(drop_period_days), 1)
    minimum_price_usd = max(minimum_price_usd, 0.0)
    initial_price_usd = max(initial_price_usd, minimum_price_usd)

    daily_drop = (initial_price_usd - minimum_price_usd) / drop_period_days

    product.price_initial_usd = initial_price_usd
    product.price_initial_usdt = initial_price_usd * DEFAULT_USDT_RATE
    product.price_minimum_usd = minimum_price_usd
    product.price_minimum_usdt = minimum_price_usd * DEFAULT_USDT_RATE
    product.price_drop_per_day_usd = daily_drop
    product.price_drop_per_day_usdt = daily_drop * DEFAULT_USDT_RATE
    product.drop_period_days = drop_period_days
    product.price_last_calculated = datetime.utcnow()

    product.price_usd = initial_price_usd
    product.price_usdt = initial_price_usd * DEFAULT_USDT_RATE

    db.commit()


def update_all_product_prices(db) -> None:
    products = db.query(Product).all()
    for product in products:
        product.price_usd = calculate_current_price(product, "USD")
        product.price_usdt = calculate_current_price(product, "USDT")
        product.price_last_calculated = datetime.utcnow()
    db.commit()


def convert_usd_to_usdt(usd_amount: float, rate: float = DEFAULT_USDT_RATE) -> float:
    return round(usd_amount * rate, 2)


def convert_usdt_to_usd(usdt_amount: float, rate: float = DEFAULT_USDT_RATE) -> float:
    if rate == 0:
        return 0.0
    return round(usdt_amount / rate, 2)


def format_price(amount: float, currency: str = "USD") -> str:
    if currency == "USD":
        return f"${amount:.2f}"
    if currency == "USDT":
        return f"{amount:.2f} USDT"
    return f"{amount:.2f} {currency}"


def calculate_referral_bonus(order_amount: float, commission_rate: float = 0.1) -> float:
    return round(order_amount * commission_rate, 2)
