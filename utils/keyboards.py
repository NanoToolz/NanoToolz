"""
Keyboard builder utility.

Provides helpers for creating inline and reply keyboards.
"""

from typing import Optional
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


class KeyboardBuilder:
    """
    Helper class for building keyboards.
    
    Simplifies creation of inline and reply keyboards with common patterns.
    """
    
    @staticmethod
    def build_inline_keyboard(
        buttons: list[list[tuple[str, str]]],
        resize: bool = True
    ) -> InlineKeyboardMarkup:
        """
        Build inline keyboard from button data.
        
        Args:
            buttons: List of button rows, each containing (text, callback_data) tuples
            resize: Whether to resize keyboard
            
        Returns:
            InlineKeyboardMarkup: Built keyboard
        """
        # TODO: Create InlineKeyboardBuilder
        # TODO: Add buttons row by row
        # TODO: Return keyboard markup
        pass
    
    @staticmethod
    def build_reply_keyboard(
        buttons: list[list[str]],
        resize: bool = True,
        one_time: bool = False
    ) -> ReplyKeyboardMarkup:
        """
        Build reply keyboard from button data.
        
        Args:
            buttons: List of button rows, each containing button texts
            resize: Whether to resize keyboard
            one_time: Whether keyboard should hide after use
            
        Returns:
            ReplyKeyboardMarkup: Built keyboard
        """
        # TODO: Create ReplyKeyboardBuilder
        # TODO: Add buttons row by row
        # TODO: Return keyboard markup
        pass
    
    @staticmethod
    def create_main_menu() -> InlineKeyboardMarkup:
        """
        Create main menu keyboard.
        
        Returns:
            InlineKeyboardMarkup: Main menu keyboard
        """
        # TODO: Define main menu buttons
        # TODO: Build and return keyboard
        pass
    
    @staticmethod
    def create_back_button(callback_data: str = "back") -> InlineKeyboardMarkup:
        """
        Create keyboard with single back button.
        
        Args:
            callback_data: Callback data for back button
            
        Returns:
            InlineKeyboardMarkup: Keyboard with back button
        """
        # TODO: Create keyboard with back button
        pass


__all__ = ["KeyboardBuilder"]
