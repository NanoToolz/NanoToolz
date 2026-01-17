"""
Callbacks handlers package initialization.

Exports the main router for all callback query handlers.
"""

from aiogram import Router

# Create router for all callback query handlers
router = Router(name="callbacks")

# TODO: Import and include specific callback handler routers
# from .main_menu import router as menu_router
# router.include_router(menu_router)

__all__ = ["router"]
