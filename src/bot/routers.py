from aiogram import Dispatcher

from src.bot.features.start.handlers import router as start_router
from src.bot.features.catalog.handlers import router as catalog_router
from src.bot.features.cart.handlers import router as cart_router
from src.bot.features.checkout.handlers import router as checkout_router
from src.bot.features.profile.handlers import router as profile_router
from src.bot.features.topup.handlers import router as topup_router
from src.bot.features.admin.handlers import router as admin_router

def setup_routers(dp: Dispatcher) -> None:
    """Register all routers"""
    # Specific features first
    dp.include_router(admin_router)
    dp.include_router(catalog_router)
    dp.include_router(cart_router)
    dp.include_router(checkout_router)
    dp.include_router(profile_router)
    dp.include_router(topup_router)
    
    # Start handler last (command handlers)
    dp.include_router(start_router)