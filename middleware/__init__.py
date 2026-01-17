"""
Middleware package initialization.

This package contains middleware for the bot including:
- Authentication and authorization
- Logging and monitoring
- Rate limiting
- User tracking
"""

from .auth_middleware import AuthMiddleware
from .logging_middleware import LoggingMiddleware

__all__ = ["AuthMiddleware", "LoggingMiddleware"]
