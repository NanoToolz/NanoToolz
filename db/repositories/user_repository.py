"""
User repository module.

Handles database operations for user data.
"""

from typing import Optional
from datetime import datetime

from db.base_repository import BaseRepository


class UserRepository(BaseRepository):
    """
    Repository for user data operations.
    
    Manages user documents in MongoDB including creation, retrieval, and updates.
    """
    
    def __init__(self):
        """Initialize user repository with 'users' collection."""
        super().__init__("users")
    
    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[dict]:
        """
        Get user by Telegram ID.
        
        Args:
            telegram_id: Telegram user ID
            
        Returns:
            Optional[dict]: User document or None if not found
        """
        # TODO: Find user by telegram_id field
        pass
    
    async def create_user(
        self,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ) -> str:
        """
        Create new user.
        
        Args:
            telegram_id: Telegram user ID
            username: Telegram username
            first_name: User's first name
            last_name: User's last name
            
        Returns:
            str: Created user document ID
        """
        # TODO: Create user document with provided data
        # TODO: Add created_at timestamp
        # TODO: Insert into database
        pass
    
    async def update_user_activity(self, telegram_id: int) -> bool:
        """
        Update user's last activity timestamp.
        
        Args:
            telegram_id: Telegram user ID
            
        Returns:
            bool: True if updated successfully
        """
        # TODO: Update last_activity field with current timestamp
        pass
    
    async def is_user_admin(self, telegram_id: int) -> bool:
        """
        Check if user is an admin.
        
        Args:
            telegram_id: Telegram user ID
            
        Returns:
            bool: True if user is admin
        """
        # TODO: Check if telegram_id is in admin list from settings
        pass
