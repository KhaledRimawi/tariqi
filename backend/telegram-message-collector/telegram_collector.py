#!/usr/bin/env python3
"""
Telegram Message Collector Script

This script connects to Telegram using Telethon library and collects messages
from specified groups or channels, saving them to both console and CSV file.

Author: GitHub Copilot
Date: July 30, 2025
"""

import asyncio
import csv
import os
import sys
import re
from datetime import datetime
import pytz
from typing import List, Dict, Any, Tuple

from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.types import Channel, Chat


class TelegramMessageCollector:
    """
    A class to collect messages from Telegram groups/channels using Telethon.
    """
    
    def __init__(self, api_id: int, api_hash: str, session_name: str = 'telegram_session'):
        """
        Initialize the Telegram client.
        
        Args:
            api_id (int): Telegram API ID
            api_hash (str): Telegram API Hash
            session_name (str): Name for the session file
        """
        self.api_id = api_id
        self.api_hash = api_hash
        self.session_name = session_name
        self.client = TelegramClient(session_name, api_id, api_hash)
        
        # Location mapping for Palestinian checkpoints and cities
        self.location_mapping = {
            'عين سينيا': {'city': 'عين سينيا', 'governorate': 'رام الله'},
            'قلنديا': {'city': 'قلنديا', 'governorate': 'رام الله'},
            'يبرود': {'city': 'يبرود', 'governorate': 'رام الله'},
            'صرة': {'city': 'صرة', 'governorate': 'نابلس'},
            'صره': {'city': 'صرة', 'governorate': 'نابلس'},
            'حارس': {'city': 'حارس', 'governorate': 'سلفيت'},
            'جبع': {'city': 'جبع', 'governorate': 'رام الله'},
            'النبي يونس': {'city': 'كفل حارس', 'governorate': 'سلفيت'},
            'بزاريا': {'city': 'بزاريا', 'governorate': 'نابلس'},
            'سيكال': {'city': 'سيكال', 'governorate': 'رام الله'},
            'واد قانا': {'city': 'واد قانا', 'governorate': 'سلفيت'},
            'واد كانا': {'city': 'واد قانا', 'governorate': 'سلفيت'},
            'كدوميم': {'city': 'كدوميم', 'governorate': 'سلفيت'},
            'قدوميم': {'city': 'كدوميم', 'governorate': 'سلفيت'},
            'العروب': {'city': 'العروب', 'governorate': 'الخليل'},
            'الطنيب': {'city': 'الطنيب', 'governorate': 'رام الله'},
            'بيت فوريك': {'city': 'بيت فوريك', 'governorate': 'نابلس'},
            'الجلزون': {'city': 'الجلزون', 'governorate': 'رام الله'},
            'رام الله': {'city': 'رام الله', 'governorate': 'رام الله'},
            'دوار الرام': {'city': 'الرام', 'governorate': 'القدس'},
            'المربعة': {'city': 'المربعة', 'governorate': 'رام الله'},
            'يتسهار': {'city': 'يتسهار', 'governorate': 'نابلس'},
            'الفحص': {'city': 'الفحص', 'governorate': 'رام الله'},
            'راس الجورة': {'city': 'راس الجورة', 'governorate': 'الخليل'},
            'فرش الهوى': {'city': 'فرش الهوى', 'governorate': 'الخليل'},
            'العيزرية': {'city': 'العيزرية', 'governorate': 'القدس'},
            'زعيم': {'city': 'زعيم', 'governorate': 'القدس'},
            'عناتا': {'city': 'عناتا', 'governorate': 'القدس'},
            'حزما': {'city': 'حزما', 'governorate': 'القدس'},
            'عناب': {'city': 'عناب', 'governorate': 'جنين'},
            'دير استيا': {'city': 'دير استيا', 'governorate': 'سلفيت'},
            'ديراستيا': {'city': 'دير استيا', 'governorate': 'سلفيت'},
            'الفندق': {'city': 'الفندق', 'governorate': 'نابلس'},
            'الرام': {'city': 'الرام', 'governorate': 'القدس'},
            'كفر عقب': {'city': 'كفر عقب', 'governorate': 'القدس'},
            'عش الغراب': {'city': 'عش الغراب', 'governorate': 'رام الله'},
            'عورتا': {'city': 'عورتا', 'governorate': 'نابلس'},
            'سلواد': {'city': 'سلواد', 'governorate': 'رام الله'},
            'دير جرير': {'city': 'دير جرير', 'governorate': 'رام الله'},
            'حومش': {'city': 'حومش', 'governorate': 'جنين'}
        }
    
    def parse_message_structure(self, message_text: str) -> Tuple[str, str, str, str]:
        """
        Parse message text to extract checkpoint name, city, event type, and remaining text.
        
        Args:
            message_text (str): Original message text
            
        Returns:
            Tuple[str, str, str, str]: (checkpoint_name, city, event_type, cleaned_text)
        """
        if not message_text:
            return 'غير محدد', 'غير محدد', 'غير محدد', ''
            
        message_lower = message_text.lower()
        
        # Extract checkpoint/location
        checkpoint_name = 'غير محدد'
        city = 'غير محدد'
        
        # Check for exact matches first
        for location, info in self.location_mapping.items():
            if location.lower() in message_lower:
                checkpoint_name = location
                city = info['city']
                break
        
        # If no exact match, try partial matches
        if checkpoint_name == 'غير محدد':
            for location, info in self.location_mapping.items():
                location_words = location.lower().split()
                if any(word in message_lower for word in location_words if len(word) > 2):
                    checkpoint_name = location
                    city = info['city']
                    break
        
        # Extract event type
        event_type = 'غير محدد'
        if any(closed in message_lower for closed in ['مغلق', 'مسكر', 'اغلاق', 'سكر', 'مغلقة', 'مسكرة', '❌']):
            event_type = 'إغلاق'
        elif any(jam in message_lower for jam in ['ازمة', 'أزمة', 'كثافة سير', 'واقف', 'خانقة', 'طويلة', '🔴']):
            event_type = 'أزمة'
        elif any(clear in message_lower for clear in ['سالك', 'سالكة', 'فاتح', 'مفتوح', 'بحري', 'نضيف', '✅']):
            event_type = 'سالك'
        elif any(checkpoint in message_lower for checkpoint in ['حاجز', 'تفتيش', 'بفتش', 'تواجد جيش', 'جيش']):
            event_type = 'حاجز/تفتيش'
        elif any(accident in message_lower for accident in ['حادث', 'حريق', 'عطلان', 'عطلانه']):
            event_type = 'حادث'
        elif any(opened in message_lower for opened in ['فتح', 'تم فتح']):
            event_type = 'فتح'
        
        # Clean the text (remove emojis and extra spaces)
        cleaned_text = re.sub(r'[🔴❌✅️🤍🤝]+', '', message_text)
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        
        return checkpoint_name, city, event_type, cleaned_text
        
    async def authenticate(self, phone_number: str = None):
        """
        Authenticate with Telegram.
        
        Args:
            phone_number (str): Phone number for authentication
        """
        await self.client.start()
        
        if not await self.client.is_user_authorized():
            if not phone_number:
                phone_number = input("Please enter your phone number (with country code): ")
            
            await self.client.send_code_request(phone_number)
            code = input("Please enter the code you received: ")
            
            try:
                await self.client.sign_in(phone_number, code)
            except SessionPasswordNeededError:
                password = input("Two-factor authentication enabled. Please enter your password: ")
                await self.client.sign_in(password=password)
        
        print("✅ Successfully authenticated with Telegram!")
    
    async def get_entity_info(self, group_username: str):
        """
        Get information about the group/channel.
        
        Args:
            group_username (str): Username or invite link of the group/channel
            
        Returns:
            Entity information
        """
        try:
            entity = await self.client.get_entity(group_username)
            
            if isinstance(entity, Channel):
                entity_type = "Channel" if entity.broadcast else "Group"
            elif isinstance(entity, Chat):
                entity_type = "Group"
            else:
                entity_type = "Unknown"
            
            print(f"📋 Found {entity_type}: {entity.title}")
            print(f"📊 Participants: {getattr(entity, 'participants_count', 'Unknown')}")
            
            return entity
        except Exception as e:
            print(f"❌ Error finding group/channel: {e}")
            return None
    
    async def collect_messages(self, group_username: str, message_limit: int, enhanced_format: bool = False) -> List[Dict[str, Any]]:
        """
        Collect messages from the specified group/channel.
        
        Args:
            group_username (str): Username or invite link of the group/channel
            message_limit (int): Number of messages to collect
            enhanced_format (bool): If True, parse message structure; if False, use normal format
            
        Returns:
            List of message dictionaries
        """
        try:
            entity = await self.get_entity_info(group_username)
            if not entity:
                return []
            
            print(f"📥 Collecting last {message_limit} messages...")
            if enhanced_format:
                print("🔧 Using enhanced format (structured parsing)")
            else:
                print("📋 Using normal format (original structure)")
            
            messages = []
            # تحديد المنطقة الزمنية (فلسطين/القدس)
            palestine_tz = pytz.timezone('Asia/Jerusalem')
            
            async for message in self.client.iter_messages(entity, limit=message_limit):
                # Skip empty messages or service messages
                if not message.text and not message.message:
                    continue
                
                # تحويل الوقت للمنطقة الزمنية المحلية
                local_time = ""
                if message.date:
                    # تحويل من UTC إلى التوقيت المحلي
                    utc_time = message.date.replace(tzinfo=pytz.UTC)
                    local_time = utc_time.astimezone(palestine_tz).strftime('%Y-%m-%d %H:%M:%S')
                
                message_text = message.text or message.message or ''
                
                if enhanced_format:
                    # Parse message structure
                    checkpoint_name, city, event_type, cleaned_text = self.parse_message_structure(message_text)
                    
                    message_data = {
                        'message_id': message.id,
                        'sender_id': message.sender_id if message.sender_id else 'Unknown',
                        'sender_name': '',
                        'checkpoint_name': checkpoint_name,
                        'city': city,
                        'event_type': event_type,
                        'original_message': message_text,
                        'cleaned_message': cleaned_text,
                        'message_date': local_time,
                        'message_type': 'text'
                    }
                else:
                    # Normal format
                    message_data = {
                        'message_id': message.id,
                        'sender_id': message.sender_id if message.sender_id else 'Unknown',
                        'sender_name': '',
                        'message_text': message_text,
                        'message_date': local_time,
                        'message_type': 'text'
                    }
                
                # Try to get sender name
                try:
                    if message.sender:
                        if hasattr(message.sender, 'first_name'):
                            first_name = message.sender.first_name or ''
                            last_name = message.sender.last_name or ''
                            message_data['sender_name'] = f"{first_name} {last_name}".strip()
                        elif hasattr(message.sender, 'title'):
                            message_data['sender_name'] = message.sender.title
                        elif hasattr(message.sender, 'username'):
                            message_data['sender_name'] = message.sender.username or 'Unknown'
                except:
                    message_data['sender_name'] = 'Unknown'
                
                # Check if message has media
                if message.media:
                    message_data['message_type'] = 'media'
                    if enhanced_format:
                        if not message_data.get('original_message'):
                            message_data['original_message'] = '[Media message]'
                            message_data['cleaned_message'] = '[Media message]'
                    else:
                        if not message_data.get('message_text'):
                            message_data['message_text'] = '[Media message]'
                
                messages.append(message_data)
            
            print(f"✅ Successfully collected {len(messages)} messages!")
            return messages
            
        except Exception as e:
            print(f"❌ Error collecting messages: {e}")
            return []
    
    def save_to_csv(self, messages: List[Dict[str, Any]], filename: str = None):
        """
        Save messages to a CSV file.
        
        Args:
            messages (List[Dict]): List of message dictionaries
            filename (str): Output filename (optional)
        """
        if not messages:
            print("⚠️ No messages to save.")
            return
        
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"telegram_messages_{timestamp}.csv"
        
        # Check if enhanced format is used
        enhanced_format = 'checkpoint_name' in messages[0] if messages else False
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                if enhanced_format:
                    # Enhanced format columns
                    fieldnames = ['message_id', 'sender_id', 'sender_name', 'checkpoint_name', 
                                'city', 'event_type', 'original_message', 'cleaned_message', 
                                'message_date', 'message_type']
                else:
                    # Normal format columns
                    fieldnames = ['message_id', 'sender_id', 'sender_name', 'message_text', 
                                'message_date', 'message_type']
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for message in messages:
                    writer.writerow(message)
            
            print(f"💾 Messages saved to: {filename}")
            
        except Exception as e:
            print(f"❌ Error saving to CSV: {e}")
    
    def print_messages(self, messages: List[Dict[str, Any]], max_display: int = 10):
        """
        Print messages to console in a formatted way.
        
        Args:
            messages (List[Dict]): List of message dictionaries
            max_display (int): Maximum number of messages to display
        """
        if not messages:
            print("⚠️ No messages to display.")
            return
        
        # Check if enhanced format is used
        enhanced_format = 'checkpoint_name' in messages[0] if messages else False
        
        print(f"\n📱 Displaying last {min(len(messages), max_display)} messages:")
        if enhanced_format:
            print("🔧 Enhanced Format (Structured)")
        else:
            print("📋 Normal Format")
        print("=" * 80)
        
        for i, msg in enumerate(messages[:max_display]):
            print(f"\n📧 Message {i+1}:")
            print(f"🆔 ID: {msg['message_id']}")
            print(f"👤 Sender: {msg['sender_name']} (ID: {msg['sender_id']})")
            print(f"📅 Date: {msg['message_date']}")
            print(f"📝 Type: {msg['message_type']}")
            
            if enhanced_format:
                print(f"� Checkpoint: {msg['checkpoint_name']}")
                print(f"🏙️ City: {msg['city']}")
                print(f"🎯 Event Type: {msg['event_type']}")
                print(f"💬 Original: {msg['original_message'][:200]}{'...' if len(msg['original_message']) > 200 else ''}")
                print(f"🧹 Cleaned: {msg['cleaned_message'][:200]}{'...' if len(msg['cleaned_message']) > 200 else ''}")
            else:
                print(f"�💬 Text: {msg['message_text'][:200]}{'...' if len(msg['message_text']) > 200 else ''}")
            
            print("-" * 40)
        
        if len(messages) > max_display:
            print(f"\n... and {len(messages) - max_display} more messages (saved to CSV)")
    
    async def close(self):
        """Close the Telegram client connection."""
        await self.client.disconnect()


async def main():
    """
    Main function to run the Telegram message collector.
    """
    # Configuration
    API_ID = 26389903
    API_HASH = "b7f2c7e63f08653def683baef7c2334b"
    
    print("🚀 Telegram Message Collector")
    print("=" * 40)
    
    # Initialize collector
    collector = TelegramMessageCollector(API_ID, API_HASH)
    
    try:
        # Authenticate
        await collector.authenticate()
        
        # Get user input
        print("\n📋 Configuration:")
        group_username = input("Enter group/channel username or invite link: ").strip()
        
        while True:
            try:
                message_limit = int(input("Enter number of messages to collect: ").strip())
                if message_limit > 0:
                    break
                else:
                    print("Please enter a positive number.")
            except ValueError:
                print("Please enter a valid number.")
        
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
        
        # Collect messages
        messages = await collector.collect_messages(group_username, message_limit, enhanced_format)
        
        if messages:
            # Display messages
            collector.print_messages(messages)
            
            # Save to CSV
            save_csv = input("\n💾 Save messages to CSV file? (y/n): ").strip().lower()
            if save_csv in ['y', 'yes']:
                custom_filename = input("Enter filename (press Enter for auto-generated): ").strip()
                filename = custom_filename if custom_filename else None
                collector.save_to_csv(messages, filename)
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Script interrupted by user.")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
    finally:
        # Clean up
        await collector.close()
        print("\n👋 Script completed. Session saved for future use.")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
