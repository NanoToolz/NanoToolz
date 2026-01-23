"""Pricing, currency conversion, and referral helpers."""


async def get_usdt_rate() -> float:
    """Get current USDT to USD rate from CoinGecko API"""
    import aiohttp

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.coingecko.com/api/v3/simple/price?ids=tether&vs_currencies=usd"
            ) as resp:
                data = await resp.json()
                return float(data["tether"]["usd"])
    except Exception as exc:
        print(f"Error fetching USDT rate: {exc}")
        return 1.0


def convert_usd_to_usdt(usd_amount: float) -> float:
    """Convert USD to USDT (1:1 + small fees)."""
    return round(usd_amount * 1.005, 2)


def convert_usdt_to_usd(usdt_amount: float) -> float:
    """Convert USDT to USD."""
    return round(usdt_amount / 1.005, 2)


def format_price(amount: float, currency: str = "USD") -> str:
    """Format price for display."""
    if currency == "USD":
        return f"${amount:.2f}"
    if currency == "EUR":
        return f"€{amount:.2f}"
    if currency == "PKR":
        return f"Rs {amount:.2f}"
    return f"{amount:.2f} {currency}"


def calculate_referral_bonus(order_amount: float, commission_rate: float = 0.1) -> float:
    """Calculate referral commission."""
    return round(order_amount * commission_rate, 2)
