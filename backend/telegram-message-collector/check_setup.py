#!/usr/bin/env python3
"""
Validation script to check if all dependencies are properly installed.
"""
import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# Reading variables from the environment
API_ID = os.getenv("TELEGRAM_API_ID")

# Verify that the values exist
if not API_ID:
    raise ValueError("❌ API ID is missing in .env file")

def check_dependencies():
    """Check if all required dependencies are available."""
    print("🔍 Checking dependencies...")
    
    try:
        import telethon
        print(f"✅ Telethon: {telethon.__version__}")
    except ImportError as e:
        print(f"❌ Telethon: Not installed - {e}")
        return False
    
    try:
        import pandas
        print(f"✅ Pandas: {pandas.__version__}")
    except ImportError as e:
        print(f"❌ Pandas: Not installed - {e}")
        return False
    
    try:
        import aiofiles
        print(f"✅ Aiofiles: {aiofiles.__version__}")
    except ImportError as e:
        print(f"❌ Aiofiles: Not installed - {e}")
        return False
    
    # Check standard library modules
    try:
        import asyncio
        import csv
        import os
        import sys
        from datetime import datetime
        print("✅ Standard library modules: OK")
    except ImportError as e:
        print(f"❌ Standard library modules: {e}")
        return False
    
    return True

def main():
    print("🧪 Telegram Message Collector - Dependency Check")
    print("=" * 50)
    
    if check_dependencies():
        print("\n🎉 All dependencies are properly installed!")
        print("✅ You can now run: python telegram_collector.py")
    else:
        print("\n❌ Some dependencies are missing.")
        print("💡 Please run: pip install -r requirements.txt")
    
    print("\n📋 Your configuration:")
    print(f"API ID: {API_ID}")
    print(f"API Hash: b7f2c7e63f08653def683baef7c2334b")
    
    print("\n📝 Next steps:")
    print("1. Run the main script: python telegram_collector.py")
    print("2. Enter your phone number when prompted")
    print("3. Enter the verification code from Telegram")
    print("4. Specify the group/channel and number of messages")

if __name__ == "__main__":
    main()
