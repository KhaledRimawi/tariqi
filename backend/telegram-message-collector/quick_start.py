#!/usr/bin/env python3
"""
Quick Start Script for Telegram Message Collector

This script provides a simplified interface for common use cases.
"""

import asyncio
import sys
import os

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram_collector import TelegramMessageCollector


async def quick_start():
    """Quick start with predefined options."""
    print("🚀 Telegram Message Collector - Quick Start")
    print("=" * 50)
    
    # API credentials
    API_ID = 26389903
    API_HASH = "b7f2c7e63f08653def683baef7c2334b"
    
    collector = TelegramMessageCollector(API_ID, API_HASH)
    
    try:
        # Authenticate
        print("🔐 Authenticating...")
        await collector.authenticate()
        
        # Quick options menu
        print("\n📋 Quick Start Options:")
        print("1. Collect from multiple channels (custom amount)")
        print("2. Collect from a single channel (custom amount)")
        print("3. Test with Telegram official channel (5 messages)")
        
        choice = input("Choose an option (1-3): ").strip()
        
        # Choose output format
        print("\n📊 Choose output format:")
        print("1. Normal format (original message structure)")
        print("2. Enhanced format (structured parsing: checkpoint, city, event type)")
        
        while True:
            format_choice = input("Select format (1 or 2): ").strip()
            if format_choice in ['1', '2']:
                enhanced_format = format_choice == '2'
                break
            else:
                print("Please enter 1 or 2.")
        
        if choice == "1":
            # Multiple channels
            print("\n📡 Enter multiple channels/groups:")
            print("You can enter channel usernames, links, or Arabic names")
            print("Press Enter twice when done")
            
            channels_list = []
            while True:
                channel_input = input(f"Channel {len(channels_list) + 1} (or press Enter to finish): ").strip()
                if not channel_input:
                    break
                channels_list.append(channel_input)
                print(f"✅ Added: {channel_input}")
            
            if not channels_list:
                print("❌ No channels provided.")
                return
            
            count = int(input("Enter number of messages per channel: ").strip())
            messages = await collector.collect_from_multiple_sources(channels_list, count, enhanced_format)
            
        elif choice == "2":
            # Single channel
            channel = input("Enter channel username (e.g., @channelname): ").strip()
            count = int(input("Enter number of messages: ").strip())
            messages = await collector.collect_messages(channel, count, enhanced_format)
            
        elif choice == "3":
            print("📋 Testing with @telegram (official Telegram channel)...")
            messages = await collector.collect_messages("telegram", 5, enhanced_format)
        else:
            print("❌ Invalid choice")
            return
        
        if messages:
            # Display results
            collector.print_messages(messages)
            
            # Auto-save to CSV
            print("\n💾 Saving to CSV...")
            collector.save_to_csv(messages)
            
            print(f"\n✅ Success! Collected {len(messages)} messages.")
        else:
            print("❌ No messages collected.")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await collector.close()


def main():
    """Main function with menu."""
    print("Select mode:")
    print("1. Quick Start (simplified)")
    print("2. Full Script (all features)")
    
    choice = input("Choose (1-2): ").strip()
    
    if choice == "1":
        asyncio.run(quick_start())
    elif choice == "2":
        print("Starting full script...")
        os.system("python telegram_collector.py")
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()
