import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")

    ADMIN_IDS_STR = os.getenv("ADMIN_IDS", "")
    ADMIN_IDS = [int(id.strip()) for id in ADMIN_IDS_STR.split(",") if id.strip()]

    SUPABASE_URL = os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL", "")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY", "")

    REFERRAL_COMMISSION = int(os.getenv("REFERRAL_COMMISSION", "10"))

    TIER_THRESHOLDS = {
        "bronze": 0,
        "silver": 50,
        "gold": 200,
        "platinum": 500
    }

settings = Settings()
