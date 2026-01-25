"""
NanoToolz Bot - High-Performance JSON Edition
Main Entry Point
"""
import asyncio
import logging
from src.bot.app import start_bot

# Simple logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

if __name__ == "__main__":
    try:
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        print("Bot stopped by user")
    except Exception as e:
        print(f"Critial Error: {e}")