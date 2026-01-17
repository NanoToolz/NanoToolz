"""
Error handlers package.

Handles various types of errors that can occur during bot operation.
"""

from aiogram import Router
from aiogram.types import ErrorEvent
import logging

logger = logging.getLogger(__name__)

# Create router for error handlers
router = Router(name="errors")


@router.error()
async def error_handler(event: ErrorEvent) -> None:
    """
    Handle all uncaught errors.
    
    Args:
        event: Error event containing exception and update info
    """
    # TODO: Log error with context
    # TODO: Send user-friendly error message
    # TODO: Notify admins for critical errors
    
    logger.error(
        f"Error: {event.exception}",
        exc_info=event.exception
    )


__all__ = ["router"]
