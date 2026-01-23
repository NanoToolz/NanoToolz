from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from .routers import include_routers


def create_dispatcher() -> Dispatcher:
    """Create dispatcher with feature routers"""
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    include_routers(dp)
    return dp
