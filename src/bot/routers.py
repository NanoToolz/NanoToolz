from aiogram import Dispatcher

from src.bot.features.help.handlers import router as help_router
from src.bot.features.catalog.handlers import router as catalog_router
from src.bot.features.cart.handlers import router as cart_router
from src.bot.features.checkout.handlers import router as checkout_router
from src.bot.features.wishlist.handlers import router as wishlist_router
from src.bot.features.profile.handlers import router as profile_router
from src.bot.features.rewards.handlers import router as rewards_router
from src.bot.features.referral.handlers import router as referral_router
from src.bot.features.support.handlers import router as support_router
from src.bot.features.start.handlers import router as start_router


def include_routers(dp: Dispatcher) -> None:
    dp.include_router(start_router)
    dp.include_router(help_router)
    dp.include_router(catalog_router)
    dp.include_router(cart_router)
    dp.include_router(checkout_router)
    dp.include_router(wishlist_router)
    dp.include_router(profile_router)
    dp.include_router(rewards_router)
    dp.include_router(referral_router)
    dp.include_router(support_router)
    dp.include_router(start_router)
