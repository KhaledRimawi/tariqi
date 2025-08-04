#!/usr/bin/env python3
"""
Simple example script to test Telegram connection and basic functionality.

This script demonstrates basic usage of the TelegramMessageCollector.
"""

import asyncio
import sys
import os

# Add the current directory to the path so we can import our module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram_collector import TelegramMessageCollector


async def quick_test():
    """
    Quick test function to verify the setup works.
    """
    print("🧪 Quick Test - Telegram Message Collector")
    print("=" * 50)
    
    # Your API credentials (already configured)
    API_ID = 26389903
    API_HASH = "b7f2c7e63f08653def683baef7c2334b"
    
    # Initialize collector
    collector = TelegramMessageCollector(API_ID, API_HASH, 'test_session')
    
    try:
        print("🔐 Testing authentication...")
        await collector.authenticate()
        
        print("✅ Authentication successful!")
        print("🎉 Setup is working correctly!")
        
        # Test with a public channel (Telegram's official channel)
        print("\n📋 Testing with Telegram's official channel...")
        test_channel = "telegram"  # Official Telegram channel
        
        entity = await collector.get_entity_info(test_channel)
        if entity:
            print("✅ Successfully found the test channel!")
            
            # Collect just 3 messages as a test
            print("📥 Collecting 3 test messages...")
            messages = await collector.collect_messages(test_channel, 3)
            
            if messages:
                print(f"✅ Successfully collected {len(messages)} messages!")
                collector.print_messages(messages, max_display=3)
            else:
                print("⚠️ No messages collected, but connection works!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print("💡 This might be normal if you haven't authenticated yet.")
        print("💡 Try running the main script: python telegram_collector.py")
    
    finally:
        await collector.close()
        print("\n🏁 Test completed!")


if __name__ == "__main__":
    asyncio.run(quick_test())
