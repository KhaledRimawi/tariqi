#!/usr/bin/env python3
"""
Quick test script for the enhanced message format
"""

import sys
import os

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram_collector import TelegramMessageCollector

def test_enhanced_format():
    """Test the enhanced format parsing"""
    print("🧪 Testing Enhanced Format Parsing")
    print("=" * 50)
    
    # Initialize collector
    collector = TelegramMessageCollector(26389903, "b7f2c7e63f08653def683baef7c2334b")
    
    # Test messages
    test_messages = [
        "المربعة سالكة بالاتجاهين بدون جيش ✅️✅️",
        "نزول يتسهار ازمة طويلة 🔴🔴🔴🔴",
        "راس الجورة مغلق❌",
        "الفحص سالك✅",
        "عش الغراب تواجد جيش شكلو ضابط المنطقه"
    ]
    
    print("\n🔍 Testing message parsing:")
    for i, message in enumerate(test_messages, 1):
        checkpoint, city, event_type, cleaned = collector.parse_message_structure(message)
        
        print(f"\n📧 Test Message {i}:")
        print(f"   Original: {message}")
        print(f"   📍 Checkpoint: {checkpoint}")
        print(f"   🏙️ City: {city}")
        print(f"   🎯 Event Type: {event_type}")
        print(f"   🧹 Cleaned: {cleaned}")
        print("-" * 40)
    
    print("\n✅ Parsing test completed!")
    print("\n💡 The enhanced format should now work correctly.")
    print("🚀 You can now run the collector with option 2 (Enhanced format)")

if __name__ == "__main__":
    test_enhanced_format()
