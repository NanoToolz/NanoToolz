import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    # Bot
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")
    ADMIN_IDS: list = [int(x) for x in os.getenv("ADMIN_IDS", "123456789").split(",")]
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///nanotoolz.db")
    
    # Crypto
    TRON_PROVIDER_URL: str = os.getenv("TRON_PROVIDER_URL", "https://api.tronstack.cn")
    USDT_CONTRACT_ADDRESS: str = os.getenv("USDT_CONTRACT_ADDRESS", "TR7NHqjeKQxGTCi8q282JJUC8kxrRvs5Qm")
    PAYMENT_WALLET_ADDRESS: str = os.getenv("PAYMENT_WALLET_ADDRESS", "YOUR_TRON_ADDRESS")
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Web Admin
    ADMIN_SECRET_KEY: str = os.getenv("ADMIN_SECRET_KEY", "your-super-secret-key")
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "password123")
    
    # Currency
    PRIMARY_CURRENCY: str = os.getenv("PRIMARY_CURRENCY", "USD")
    EXCHANGE_RATE_API: str = os.getenv("EXCHANGE_RATE_API", "coingecko")
    
    # App
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    class Config:
        env_file = ".env"

settings = Settings()
