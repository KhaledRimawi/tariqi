#!/usr/bin/env python3
"""
Quick Start for Multi-Channel Telegram Message Collector

Simple interface to quickly start collecting from multiple Telegram channels/groups.
"""

import asyncio
import os
import sys


def print_banner():
    """Print application banner."""
    print("🚀 Multi-Channel Telegram Message Collector")
    print("=" * 50)
    print("📡 Collect from multiple channels simultaneously")
    print("🔄 Chronological sorting with source tracking")
    print("📊 Support for both normal and enhanced formats")
    print("=" * 50)


def get_channels_input():
    """Get channel list from user input."""
    print("\n📋 Channel/Group Setup:")
    print("Enter Telegram channels/groups (one per line)")
    print("Examples:")
    print("  • @channelname")
    print("  • احوال الطرق")
    print("  • https://t.me/groupname")
    print("  • group_username")
    print("\nPress Enter twice when done")
    
    channels = []
    print("\n📝 Enter channels:")
    
    while True:
        channel = input(f"Channel {len(channels) + 1} (Enter to finish): ").strip()
        
        if not channel:
            break
            
        channels.append(channel)
        print(f"✅ Added: {channel}")
    
    return channels


def get_message_count():
    """Get number of messages to collect per channel."""
    while True:
        try:
            count = int(input("\n📥 Messages per channel (e.g., 50): ").strip())
            if count > 0:
                return count
            else:
                print("❌ Please enter a positive number.")
        except ValueError:
            print("❌ Please enter a valid number.")


def get_format_choice():
    """Get output format preference."""
    print("\n📊 Output Format Options:")
    print("1. 📋 Normal Format")
    print("   • Basic message info")
    print("   • Source channel tracking")
    print("   • Standard CSV output")
    
    print("\n2. 🔧 Enhanced Format")
    print("   • Palestinian checkpoint parsing")
    print("   • Location and city extraction")
    print("   • Event type classification")
    print("   • Enhanced CSV with analysis")
    
    while True:
        choice = input("\nSelect format (1 or 2): ").strip()
        if choice in ['1', '2']:
            return choice == '2'
        else:
            print("❌ Please enter 1 or 2.")


async def run_collector():
    """Main collection function."""
    try:
        print_banner()
        
        # Get user input
        channels = get_channels_input()
        
        if not channels:
            print("❌ No channels provided. Exiting...")
            return
        
        message_count = get_message_count()
        enhanced_format = get_format_choice()
        
        # Display summary
        print("\n🎯 Collection Summary:")
        print(f"📡 Channels: {len(channels)}")
        for i, channel in enumerate(channels, 1):
            print(f"   {i}. {channel}")
        print(f"📥 Messages per channel: {message_count}")
        print(f"📊 Format: {'Enhanced' if enhanced_format else 'Normal'}")
        
        confirm = input("\n▶️ Start collection? (y/n): ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("❌ Collection cancelled.")
            return
        
        # Import and run collector
        print("\n🔄 Initializing collector...")
        from multi_channel_collector import MultiChannelTelegramCollector
        
        # Configuration
        API_ID = 26389903
        API_HASH = "b7f2c7e63f08653def683baef7c2334b"
        
        collector = MultiChannelTelegramCollector(API_ID, API_HASH)
        
        try:
            # Authenticate
            print("🔐 Authenticating with Telegram...")
            await collector.authenticate()
            
            # Collect messages
            messages = await collector.collect_from_multiple_channels(
                channels, message_count, enhanced_format
            )
            
            if messages:
                # Display sample
                collector.print_sample_messages(messages)
                
                # Auto-save with timestamp
                import datetime
                timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                format_prefix = "enhanced" if enhanced_format else "normal"
                filename = f"multi_channel_{format_prefix}_{timestamp}.csv"
                
                collector.save_to_csv(messages, filename)
                
                print(f"\n✅ Collection completed successfully!")
                print(f"📊 Total messages: {len(messages)}")
                print(f"💾 Saved to: {filename}")
                
            else:
                print("\n⚠️ No messages collected.")
                
        finally:
            await collector.close()
            
    except KeyboardInterrupt:
        print("\n⏹️ Collection interrupted by user.")
    except ImportError as e:
        print(f"\n❌ Import Error: {e}")
        print("Please ensure multi_channel_collector.py is in the same directory.")
    except Exception as e:
        print(f"\n❌ Error: {e}")


def main():
    """Entry point."""
    try:
        asyncio.run(run_collector())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
    finally:
        print("\n🏁 Program finished.")


if __name__ == "__main__":
    main()
