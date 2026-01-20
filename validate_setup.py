#!/usr/bin/env python3
"""
Quick validation script to check bot setup
"""

import os
import sys

def check_setup():
    """Check if bot is properly configured"""
    
    errors = []
    warnings = []
    
    print("🔍 Checking NanoToolz Setup...")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 10):
        errors.append(f"Python 3.10+ required, got {sys.version_info.major}.{sys.version_info.minor}")
    else:
        print("✅ Python version OK")
    
    # Check requirements
    try:
        import aiogram
        print("✅ aiogram installed")
    except ImportError:
        errors.append("aiogram not installed. Run: pip install -r requirements.txt")
    
    try:
        import fastapi
        print("✅ FastAPI installed")
    except ImportError:
        warnings.append("FastAPI not installed (needed for admin panel)")
    
    try:
        import sqlalchemy
        print("✅ SQLAlchemy installed")
    except ImportError:
        errors.append("SQLAlchemy not installed. Run: pip install -r requirements.txt")
    
    # Check .env file
    if os.path.exists(".env"):
        print("✅ .env file exists")
        
        with open(".env", "r") as f:
            content = f.read()
            if "YOUR_BOT_TOKEN" in content:
                errors.append("BOT_TOKEN not set in .env")
            else:
                print("✅ BOT_TOKEN configured")
            
            if "YOUR_TRON_ADDRESS" in content:
                warnings.append("PAYMENT_WALLET_ADDRESS not set (needed for payments)")
            else:
                print("✅ Payment wallet configured")
    else:
        errors.append(".env file not found. Run: cp .env.example .env")
    
    # Check database
    if os.path.exists("nanotoolz.db"):
        print("✅ Database exists")
    else:
        print("ℹ️  Database will be created on first run")
    
    # Print results
    print("=" * 50)
    
    if errors:
        print("\n❌ Errors:")
        for error in errors:
            print(f"  • {error}")
    
    if warnings:
        print("\n⚠️  Warnings:")
        for warning in warnings:
            print(f"  • {warning}")
    
    if not errors:
        print("\n✅ Setup looks good!")
        print("\nTo start the bot:")
        print("  python main.py")
        return True
    else:
        print("\n❌ Fix the errors above and try again")
        return False

if __name__ == "__main__":
    success = check_setup()
    sys.exit(0 if success else 1)
