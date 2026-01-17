"""
Logging middleware.

Provides structured logging for all bot updates and actions.
"""

from typing import Any, Awaitable, Callable
import logging

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update, Message, CallbackQuery

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
    """
    Middleware for logging bot updates and user actions.
    
    Logs all incoming updates with relevant context for monitoring and debugging.
    """
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any]
    ) -> Any:
        """
        Process and log incoming update.
        
        Args:
            handler: Next handler in chain
            event: Incoming event
            data: Handler data dictionary
            
        Returns:
            Any: Handler result
        """
        # TODO: Extract update info
        # TODO: Log update type and user info
        # TODO: Log execution time
        # TODO: Log any errors
        
        # Log before processing
        if isinstance(event, Message):
            logger.info(
                f"Message from user {event.from_user.id}: {event.text}"
            )
        elif isinstance(event, CallbackQuery):
            logger.info(
                f"Callback from user {event.from_user.id}: {event.data}"
            )
        
        # Process update
        result = await handler(event, data)
        
        # Log after processing
        logger.debug("Update processed successfully")
        
        return result


__all__ = ["LoggingMiddleware"]
