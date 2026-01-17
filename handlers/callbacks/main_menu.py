"""
Main menu callback handlers.

Handles callback queries from main menu inline buttons.
"""

from aiogram import Router
from aiogram.types import CallbackQuery


router = Router(name="main_menu")


# TODO: Define callback data models
# TODO: Implement callback handlers for menu actions

# Example:
# @router.callback_query(F.data == "menu_action")
# async def handle_menu_action(callback: CallbackQuery) -> None:
#     """Handle menu action callback."""
#     pass
