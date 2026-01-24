"""
Bot routers setup - registers all feature handlers
"""
from aiogram import Dispatcher, Router
from aiogram.filters.command import Command
from aiogram.types import Message

from src.bot.features.start.handlers import router as start_router
from src.bot.features.catalog.handlers import router as catalog_router
from src.bot.features.cart.handlers import router as cart_router
from src.bot.features.checkout.handlers import router as checkout_router
from src.bot.features.profile.handlers import router as profile_router
from src.bot.features.help.handlers import router as help_router
from src.bot.features.admin.handlers import router as admin_router
from src.bot.features.topup.handlers import router as topup_router
from src.bot.features.rewards.handlers import router as rewards_router
from src.bot.features.support.handlers import router as support_router

def setup_routers(dp: Dispatcher) -> None:
    """Register all routers in correct order"""
    # Order matters: more specific routers first
    dp.include_router(admin_router)
    dp.include_router(start_router)
    dp.include_router(catalog_router)
    dp.include_router(cart_router)
    dp.include_router(checkout_router)
    dp.include_router(profile_router)
    dp.include_router(help_router)
    dp.include_router(topup_router)
    dp.include_router(rewards_router)
    dp.include_router(support_router)