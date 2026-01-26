# ============================================
# BOT CONFIGURATION
# ============================================
# Load settings from environment variables

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Bot settings"""
    
    # Bot token from .env
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")
    
    # Admin IDs from .env (comma-separated)
    ADMIN_IDS_STR = os.getenv("ADMIN_IDS", "")
    ADMIN_IDS = [int(id.strip()) for id in ADMIN_IDS_STR.split(",") if id.strip()]
    
    # Database path
    DB_PATH = "data"

# Create settings instance
settings = Settings()
