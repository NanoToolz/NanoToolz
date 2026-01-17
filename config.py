"""
Configuration module for the NanoToolz bot.

Handles loading and validation of environment variables and application settings.
"""

from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    All sensitive data should be stored in .env file and loaded through this class.
    """
    
    # Bot configuration
    BOT_TOKEN: str
    ADMIN_IDS: list[int] = []
    
    # Database configuration
    MONGODB_URI: str
    MONGODB_DB_NAME: str = "nanotoolz"
    
    # Application settings
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
