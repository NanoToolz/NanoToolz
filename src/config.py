import os
from dotenv import load_dotenv
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

class Settings(BaseSettings):
    # Bot
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")
    ADMIN_IDS: list[int] = Field(default_factory=lambda: [123456789])
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///nanotoolz.db")
    
    # Crypto
    TRON_PROVIDER_URL: str = os.getenv("TRON_PROVIDER_URL", "https://api.tronstack.cn")
    USDT_CONTRACT_ADDRESS: str = os.getenv("USDT_CONTRACT_ADDRESS", "TR7NHqjeKQxGTCi8q282JJUC8kxrRvs5Qm")
    PAYMENT_WALLET_TRON: str = os.getenv("PAYMENT_WALLET_TRON", "TXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    PAYMENT_WALLET_LTC: str = os.getenv("PAYMENT_WALLET_LTC", "LXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Web Admin
    ADMIN_SECRET_KEY: str = os.getenv("ADMIN_SECRET_KEY", "your-super-secret-key")
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "password123")
    
    # Currency
    PRIMARY_CURRENCY: str = os.getenv("PRIMARY_CURRENCY", "USD")
    EXCHANGE_RATE_API: str = os.getenv("EXCHANGE_RATE_API", "coingecko")
    
    # Store
    STORE_NAME: str = os.getenv("STORE_NAME", "NanoToolz Store")
    SUPPORT_CONTACT: str = os.getenv("SUPPORT_CONTACT", "@YourSupport")

    # App
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    @field_validator("ADMIN_IDS", mode="before")
    @classmethod
    def parse_admin_ids(cls, value):
        if value is None:
            return [123456789]
        if isinstance(value, str):
            parts = [item.strip() for item in value.split(",") if item.strip()]
            return [int(item) for item in parts]
        if isinstance(value, int):
            return [value]
        if isinstance(value, (list, tuple)):
            return [int(item) for item in value]
        return value

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
