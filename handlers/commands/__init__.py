"""
Commands handlers package initialization.

Exports the main router for all command handlers.
"""

from aiogram import Router

# Create router for all command handlers
router = Router(name="commands")

# TODO: Import and include specific command handler routers
# from .start import router as start_router
# from .help import router as help_router
# router.include_router(start_router)
# router.include_router(help_router)

__all__ = ["router"]
