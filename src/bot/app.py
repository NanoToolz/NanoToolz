from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from src.middleware.ban import BanMiddleware
from .routers import include_routers


def create_dispatcher() -> Dispatcher:
    """Create dispatcher with feature routers"""
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.message.middleware(BanMiddleware())
    dp.callback_query.middleware(BanMiddleware())
    include_routers(dp)
    return dp
