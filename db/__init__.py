"""
Database package initialization.

This package handles all database operations including
connection management, models, and repositories.
"""

from .connection import Database

__all__ = ["Database"]
