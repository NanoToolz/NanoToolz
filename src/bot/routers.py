from aiogram import Dispatcher

from src.bot.features.start import router as start_router
from src.bot.features.catalog import router as catalog_router
from src.bot.features.cart import router as cart_router
from src.bot.features.checkout import router as checkout_router
from src.bot.features.profile import router as profile_router
from src.bot.features.topup import router as topup_router
from src.bot.features.admin import router as admin_router
from src.bot.features.help import router as help_router
from src.bot.features.support import router as support_router
from src.bot.features.referral import router as referral_router
from src.bot.features.rewards import router as rewards_router
from src.bot.features.wishlist import router as wishlist_router

def setup_routers(dp: Dispatcher) -> None:
    """Register all routers"""
    # Specific features first (order matters for callback matching)
    dp.include_router(admin_router)
    dp.include_router(catalog_router)
    dp.include_router(cart_router)
    dp.include_router(checkout_router)
    dp.include_router(profile_router)
    dp.include_router(topup_router)
    dp.include_router(help_router)
    dp.include_router(support_router)
    dp.include_router(referral_router)
    dp.include_router(rewards_router)
    dp.include_router(wishlist_router)
    
    # Start handler last (command handlers)
    dp.include_router(start_router)
