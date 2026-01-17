"""
Handlers package initialization.

This package contains all Telegram message handlers organized by type:
- commands: Command handlers (/start, /help, etc.)
- callbacks: Callback query handlers (inline button clicks)
- errors: Error handlers
"""

from .commands import router as commands_router
from .callbacks import router as callbacks_router
from .errors import router as errors_router

__all__ = ["commands_router", "callbacks_router", "errors_router"]
