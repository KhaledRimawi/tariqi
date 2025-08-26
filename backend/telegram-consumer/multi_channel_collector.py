import base64
import os
import sys

# resolve path to ../common relative to *this file*
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "common")))

import asyncio
import csv
import os
import re
from datetime import datetime
from typing import Any, Dict, List, Tuple

from dotenv import load_dotenv

load_dotenv()
from keyvault_client import get_secret
# Import MongoDB handler
from mongodb_handler import MongoDBHandler
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.types import Channel, Chat


class MultiChannelTelegramCollector:
    """
    Enhanced Telegram collector that supports multiple channels/groups
    """

    def __init__(self, api_id: int, api_hash: str, phone_number: str = None):
        """
        Initialize the Telegram client.

        Args:
            api_id (int): Telegram API ID
            api_hash (str): Telegram API Hash
            phone_number (str): Phone number for authentication
            session_name (str): Name for the session file
        """
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone_number = phone_number

        self.client = TelegramClient(get_session_file(), api_id, api_hash)

        # Enhanced location mapping for Palestinian checkpoints and cities
        # Format: 'checkpoint_name': {'city': 'actual_city_name'}
        self.location_mapping = {
            # منطقة نابلس
            "دير شرف": {"city": "نابلس"},
            "شافي شومرون": {"city": "نابلس"},
            "المربعة": {"city": "نابلس"},
            "بوابة بورين": {"city": "نابلس"},
            "صرة": {"city": "نابلس"},
            "عورتا": {"city": "نابلس"},
            "ال17 عصيرة": {"city": "نابلس"},
            "بيت فوريك": {"city": "نابلس"},
            "الباذان": {"city": "نابلس"},
            "زعترة": {"city": "نابلس"},
            # منطقة رام الله
            "عين سينا": {"city": "رام الله"},
            "بيت ايل": {"city": "رام الله"},
            "عطارة البلد": {"city": "رام الله"},
            "عطارة بيرزيت": {"city": "رام الله"},
            "الجلزون": {"city": "رام الله"},
            "بوابة النبي صالح": {"city": "رام الله"},
            "روابي": {"city": "رام الله"},
            "عيلي": {"city": "رام الله"},
            "عيون الحرمية": {"city": "رام الله"},
            "خربثا": {"city": "رام الله"},
            "المخماس": {"city": "رام الله"},
            "بوابة بدو": {"city": "رام الله"},
            "بوابة نعلين": {"city": "رام الله"},
            "بوابة سنجل": {"city": "رام الله"},
            # منطقة القدس
            "قلنديا": {"city": "القدس"},
            "كفر عقب": {"city": "القدس"},
            "عناتا": {"city": "القدس"},
            "جبع": {"city": "القدس"},
            "الرام": {"city": "القدس"},
            "شعفاط": {"city": "القدس"},
            "العيزرية": {"city": "القدس"},
            "حزما": {"city": "القدس"},
            # منطقة الخليل
            "راس الجورة": {"city": "الخليل"},
            "فرش الهوا": {"city": "الخليل"},
            "بني النعيم": {"city": "الخليل"},
            "الفحص": {"city": "الخليل"},
            "كرمة": {"city": "الخليل"},
            "جسر حلحول": {"city": "الخليل"},
            "خلة المية": {"city": "الخليل"},
            "العمور": {"city": "الخليل"},
            "الفوار": {"city": "الخليل"},
            "الشويكة": {"city": "الخليل"},
            "دورا": {"city": "الخليل"},
            "العروب": {"city": "الخليل"},
            "بوابة بيت امر": {"city": "الخليل"},
            "سعير": {"city": "الخليل"},
            # منطقة بيت لحم
            "الكونتينر": {"city": "بيت لحم"},
            "عش الغراب": {"city": "بيت لحم"},
            "النشاش": {"city": "بيت لحم"},
            "بيت جالا": {"city": "بيت لحم"},
            "النفق": {"city": "بيت لحم"},
            "السدر": {"city": "بيت لحم"},
            "جناتا": {"city": "بيت لحم"},
            "الخضر": {"city": "بيت لحم"},
            "العبيدية": {"city": "بيت لحم"},
            "جاحز 300": {"city": "بيت لحم"},
            "المناشير": {"city": "بيت لحم"},
            "ام سلمونة": {"city": "بيت لحم"},
            "نصار": {"city": "بيت لحم"},
            # منطقة سلفيت
            "مدخل سلفيت الشمالي": {"city": "سلفيت"},
            "ديرستيا": {"city": "سلفيت"},
            "بوابة كفل حارس": {"city": "سلفيت"},
            "بوابة حارس": {"city": "سلفيت"},
            "سدة قرواة": {"city": "سلفيت"},
            "بوابة بروقين": {"city": "سلفيت"},
            "ياسوف": {"city": "سلفيت"},
            "كدوميم": {"city": "سلفيت"},
            "واد قانا": {"city": "سلفيت"},
            "دير بلوط": {"city": "سلفيت"},
            "كفر الديك": {"city": "سلفيت"},
            "بوابة مردا الشرقية": {"city": "سلفيت"},
            "بوابة مردا الغربية": {"city": "سلفيت"},
            "اشارات ارائيل": {"city": "سلفيت"},
            "بوابة جماعين": {"city": "سلفيت"},
            # منطقة قلقيلية
            "المدخل الشرقي": {"city": "قلقيلية"},
            "نفق حبلة": {"city": "قلقيلية"},
            "مدخل اماتين": {"city": "قلقيلية"},
            "مدخل جينصافوط": {"city": "قلقيلية"},
            "جسر عزون": {"city": "قلقيلية"},
            "مدخل كفر لاقف": {"city": "قلقيلية"},
            "حجة": {"city": "قلقيلية"},
            "الفندق": {"city": "قلقيلية"},
            "مدخل النبي الياس": {"city": "قلقيلية"},
            # منطقة طولكرم
            "بزاريا": {"city": "طولكرم"},
            "عناب": {"city": "طولكرم"},
            "عنبتا": {"city": "طولكرم"},
            "سناعوز": {"city": "طولكرم"},
            "ايال": {"city": "طولكرم"},
            "جبارة": {"city": "طولكرم"},
            "قفين": {"city": "طولكرم"},
            "جبارة تحت الجسر": {"city": "طولكرم"},
            "بيت ليد": {"city": "طولكرم"},
            "مدخل رامين": {"city": "طولكرم"},
            "سهل رامين": {"city": "طولكرم"},
            "كفر اللبد": {"city": "طولكرم"},
            "شوفة": {"city": "طولكرم"},
            "حرميش": {"city": "طولكرم"},
            # منطقة جنين
            "حومش": {"city": "جنين"},
            "الجلمة": {"city": "جنين"},
            "دوتان": {"city": "جنين"},
            "برطعة": {"city": "جنين"},
            # منطقة اريحا (طوباس)
            "تياسير": {"city": "اريحا(طوباس)"},
            "الحمرا": {"city": "اريحا(طوباس)"},
            "المعرجات": {"city": "اريحا(طوباس)"},
            "معالي افرايم": {"city": "اريحا(طوباس)"},
            "الهيئة": {"city": "اريحا(طوباس)"},
            "البنانا": {"city": "اريحا(طوباس)"},
            "البوابة الصفراء": {"city": "اريحا(طوباس)"},
            "عين جدي": {"city": "اريحا(طوباس)"},
            "شارع 90": {"city": "اريحا(طوباس)"},
        }

    async def authenticate(self, phone_number: str = None):
        """
        Authenticate with Telegram.

        Args:
            phone_number (str): Phone number for authentication
        """
        # Use provided phone number or stored one
        if not phone_number and self.phone_number:
            phone_number = self.phone_number
        elif not phone_number:
            phone_number = input("📱 Enter your phone number (with country code, e.g., +970599123456): ")

        print(f"📱 Using phone number: {phone_number}")

        await self.client.connect()

        if await self.client.is_user_authorized():
            print("✅ Already authenticated from previous session!")
            return

        # Need to authenticate
        print("🔐 Authentication required...")
        await self.client.send_code_request(phone_number)
        code = input("📨 Enter the verification code sent to your phone: ")

        try:
            await self.client.sign_in(phone_number, code)
        except SessionPasswordNeededError:
            password = input("🔐 Enter your 2FA password: ")
            await self.client.sign_in(password=password)

        print("✅ Successfully authenticated!")

    async def get_entity_info(self, group_username: str):
        """
        Get entity information for a group/channel.

        Args:
            group_username (str): Username or invite link

        Returns:
            Entity object or None
        """
        try:
            entity = await self.client.get_entity(group_username)

            if isinstance(entity, Channel):
                print(f"📋 Found Channel: {entity.title}")
                print(f"📊 Participants: {entity.participants_count}")
            elif isinstance(entity, Chat):
                print(f"📋 Found Group: {entity.title}")
                print(f"📊 Participants: {entity.participants_count}")

            return entity

        except Exception as e:
            print(f"❌ Error accessing {group_username}: {e}")
            return None

    def parse_message_structure(self, message_text: str) -> Tuple[str, str, str, str]:
        """
        Parse message text to extract checkpoint name, city, event type, and remaining text.

        Args:
            message_text (str): Original message text

        Returns:
            Tuple[str, str, str, str, str]: (checkpoint_name, city, status, direction, cleaned_text)
        """
        if not message_text:
            return "غير محدد", "غير محدد", "غير محدد", "غير محدد", ""

        message_lower = message_text.lower()

        # Extract checkpoint/location
        checkpoint_name = "غير محدد"
        city = "غير محدد"

        # Check for exact matches first
        for location, info in self.location_mapping.items():
            if location.lower() in message_lower:
                checkpoint_name = location
                city = info["city"]
                break

        # If no exact match, try partial matches
        if checkpoint_name == "غير محدد":
            for location, info in self.location_mapping.items():
                location_words = location.lower().split()
                if any(word in message_lower for word in location_words if len(word) > 2):
                    checkpoint_name = location
                    city = info["city"]
                    break

        # Extract status (event type)
        status = "غير محدد"

        # Check for questions/inquiries first
        if any(word in message_lower for word in ["شو وضع", "كيف", "ايش وضع", "كيف الوضع", "؟"]):
            status = "استفسار"
        elif any(
            closed in message_lower
            for closed in [
                "مغلق",
                "مسكر",
                "اغلاق",
                "سكر",
                "مغلقة",
                "مسكرة",
                "❌",
            ]
        ):
            status = "إغلاق"
        elif any(
            jam in message_lower
            for jam in [
                "ازمة",
                "أزمة",
                "كثافة سير",
                "واقف",
                "خانقة",
                "طويلة",
                "🔴",
            ]
        ):
            status = "أزمة"
        elif any(
            clear in message_lower
            for clear in [
                "سالك",
                "سالكة",
                "فاتح",
                "مفتوح",
                "بحري",
                "نضيف",
                "✅",
            ]
        ):
            status = "سالك"
        elif any(
            checkpoint in message_lower
            for checkpoint in [
                "حاجز",
                "تفتيش",
                "بفتش",
                "تواجد جيش",
                "جيش",
                "حاجز طيار",
                "وقف",
            ]
        ):
            status = "حاجز/تفتيش"
        elif any(accident in message_lower for accident in ["حادث", "حريق", "عطلان", "عطلانه"]):
            status = "حادث"
        elif any(opened in message_lower for opened in ["فتح", "تم فتح"]):
            status = "فتح"
        # Extract direction
        direction = "غير محدد"

        # Check for direction indicators
        if any(enter in message_lower for enter in ["للداخل", "دخول", "داخل", "للدخول", "ل الداخل"]):
            direction = "دخول"
        elif any(exit in message_lower for exit in ["للخارج", "خروج", "خارج", "للخروج", "ل الخارج"]):
            direction = "خروج"
        elif any(both in message_lower for both in ["بالاتجاهين", "الاتجاهين", "الجهتين", "باتجاهين"]):
            direction = "دخول وخروج"

        # Clean the text (remove emojis and extra spaces)
        cleaned_text = re.sub(r"[🔴❌✅️🤍🤝⚠️✋]+", "", message_text)
        cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()

        return checkpoint_name, city, status, direction, cleaned_text

    async def collect_from_single_channel(
        self,
        channel_username: str,
        message_limit: int,
        enhanced_format: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Collect messages from a single channel/group.
        """
        try:
            entity = await self.get_entity_info(channel_username)
            if not entity:
                return []

            print(f"📥 Collecting {message_limit} messages from: {channel_username}")

            messages = []

            async for message in self.client.iter_messages(entity, limit=message_limit):
                if not message.text and not message.message:
                    continue

                # Convert time to local timezone
                local_time = ""
                if message.date:
                    local_time = message.date

                message_text = message.text or message.message or ""

                if enhanced_format:
                    checkpoint_name, city, status, direction, cleaned_text = self.parse_message_structure(message_text)

                    message_data = {
                        "message_id": message.id,
                        "source_channel": channel_username,
                        "original_message": message_text,
                        "checkpoint_name": checkpoint_name,
                        "city_name": city,
                        "status": status,
                        "direction": direction,
                        "message_date": local_time,
                    }
                else:
                    message_data = {
                        "message_id": message.id,
                        "sender_id": (message.sender_id if message.sender_id else "Unknown"),
                        "sender_name": "",
                        "source_channel": channel_username,
                        "message_text": message_text,
                        "message_date": local_time,
                        "message_type": "text",
                    }

                # Handle media messages
                if message.media:
                    message_data["message_type"] = "media"
                    if enhanced_format:
                        if not message_data.get("original_message"):
                            message_data["original_message"] = "[Media message]"
                            message_data["cleaned_message"] = "[Media message]"
                    else:
                        if not message_data.get("message_text"):
                            message_data["message_text"] = "[Media message]"

                messages.append(message_data)

            print(f"✅ Collected {len(messages)} messages from {channel_username}")
            return messages

        except Exception as e:
            print(f"❌ Error collecting from {channel_username}: {e}")
            return []

    async def collect_from_multiple_channels(
        self,
        channels_list: List[str],
        messages_per_channel: int,
        enhanced_format: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Collect messages from multiple channels and merge them chronologically.
        """
        all_messages = []
        successful_channels = 0

        print(f"🔄 Starting collection from {len(channels_list)} channels...")
        print("=" * 70)

        for i, channel in enumerate(channels_list, 1):
            print(f"\n📡 [{i}/{len(channels_list)}] Processing: {channel}")

            try:
                messages = await self.collect_from_single_channel(channel, messages_per_channel, enhanced_format)

                if messages:
                    all_messages.extend(messages)
                    successful_channels += 1
                    print(f"✅ Added {len(messages)} messages")
                else:
                    print("⚠️ No messages collected")

            except Exception as e:
                print(f"❌ Failed: {e}")
                continue

        if all_messages:
            # Sort chronologically (newest first)
            sorted_messages = sorted(all_messages, key=lambda x: x["message_date"], reverse=True)

            print("\n🎯 Collection Summary:")
            print(f"   📊 Total messages: {len(sorted_messages)}")
            print(f"   📡 Successful channels: {successful_channels}/{len(channels_list)}")

            if sorted_messages:
                print(f"   🕐 Latest: {sorted_messages[0]['message_date']}")
                print(f"   🕐 Oldest: {sorted_messages[-1]['message_date']}")

            # Show distribution by source
            source_count = {}
            for msg in sorted_messages:
                source = msg.get("source_channel", "Unknown")
                source_count[source] = source_count.get(source, 0) + 1

            print("\n📈 Messages per source:")
            for source, count in source_count.items():
                percentage = (count / len(sorted_messages)) * 100
                print(f"   📡 {source}: {count} ({percentage:.1f}%)")

            return sorted_messages
        else:
            print("❌ No messages collected from any source!")
            return []

    def save_to_csv(self, messages: List[Dict[str, Any]], filename: str = None):
        """Save messages to CSV file."""
        if not messages:
            print("⚠️ No messages to save.")
            return

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"multi_channel_messages_{timestamp}.csv"

        enhanced_format = "checkpoint_name" in messages[0] if messages else False

        try:
            with open(filename, "w", newline="", encoding="utf-8") as csvfile:
                if enhanced_format:
                    fieldnames = [
                        "message_id",
                        "source_channel",
                        "original_message",
                        "checkpoint_name",
                        "city_name",
                        "status",
                        "direction",
                        "message_date",
                    ]
                else:
                    fieldnames = [
                        "message_id",
                        "sender_id",
                        "sender_name",
                        "source_channel",
                        "message_text",
                        "message_date",
                        "message_type",
                    ]

                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for message in messages:
                    writer.writerow(message)

            print(f"💾 Messages saved to: {filename}")

        except Exception as e:
            print(f"❌ Error saving to CSV: {e}")

    def save_to_mongodb(self, messages: List[Dict[str, Any]]) -> bool:
        """Save messages to MongoDB database."""
        if not messages:
            print("⚠️ No messages to save to MongoDB.")
            return False

        print(f"\n💾 Saving {len(messages)} messages to MongoDB...")

        try:
            # Initialize MongoDB handler
            mongo_handler = MongoDBHandler()

            # Connect to MongoDB
            if not mongo_handler.connect():
                print("❌ Failed to connect to MongoDB")
                return False

            # Save messages
            success = mongo_handler.save_messages(messages)

            if success:
                print(f"✅ Successfully saved {len(messages)} messages to MongoDB!")

                # Get collection stats
                stats = mongo_handler.get_collection_stats()
                print(f"📊 Total documents in collection: {stats.get('total_documents', 'Unknown')}")
            else:
                print("❌ Failed to save messages to MongoDB")

            # Disconnect
            mongo_handler.disconnect()

            return success

        except Exception as e:
            print(f"❌ Error saving to MongoDB: {e}")
            return False

    def print_sample_messages(self, messages: List[Dict[str, Any]], max_display: int = 5):
        """Print sample messages to console."""
        if not messages:
            print("⚠️ No messages to display.")
            return

        enhanced_format = "checkpoint_name" in messages[0] if messages else False

        print(f"\n📱 Sample Messages (showing {min(len(messages), max_display)} of {len(messages)}):")
        if enhanced_format:
            print("🔧 Enhanced Format")
        else:
            print("📋 Normal Format")
        print("=" * 80)

        for i, msg in enumerate(messages[:max_display]):
            print(f"\n📧 Message {i + 1}:")
            print(f"🆔 ID: {msg['message_id']}")
            print(f" Source: {msg.get('source_channel', 'Unknown')}")
            print(f"📅 Date: {msg['message_date']}")

            if enhanced_format:
                print(f"📍 Checkpoint: {msg['checkpoint_name']}")
                print(f"🏙️ City: {msg['city_name']}")
                print(f"🎯 Status: {msg['status']}")
                print(f"↔️ Direction: {msg['direction']}")
                print(f"💬 Message: {msg['original_message'][:100]}...")
            else:
                print(f"💬 Text: {msg['message_text'][:100]}...")

            print("-" * 40)

    async def close(self):
        """Close the Telegram client connection."""
        await self.client.disconnect()


async def main():
    """Main function for multi-channel collection."""

    # Reading variables from the environment
    API__ID = int(os.getenv("TELEGRAM_API_ID"))

    # Verify that the values exist
    if not API__ID or not API__ID:
        raise ValueError("❌ API ID is missing in .env file")

    # Configuration
    API_ID = API__ID
    API_HASH = get_secret("appHash")

    print("🚀 Multi-Channel Telegram Message Collector")
    print("=" * 50)

    session_file_path = get_session_file()
    if not os.path.exists(session_file_path) or os.path.getsize(session_file_path) == 0:
        raise RuntimeError(f"❌ Session file missing or empty: {session_file_path}")

    collector = MultiChannelTelegramCollector(API_ID, API_HASH, get_secret("PhoneNumber"))

    try:
        # Authenticate
        await collector.authenticate()

        # Get channels input
        print("\n📋 Channel/Group Configuration:")
        print("Enter multiple channels/groups (one per line)")
        print("Examples: @channelname, احوال الطرق, https://t.me/groupname")
        print("Press Enter twice when done")

        channels_list = []
        print("\nEnter channels:")

        while True:
            channel_input = input(f"Channel {len(channels_list) + 1} (Enter to finish): ").strip()

            if not channel_input:
                break

            channels_list.append(channel_input)
            print(f"✅ Added: {channel_input}")

        if not channels_list:
            print("❌ No channels provided. Exiting...")
            return

        print(f"\n📡 Channels to process: {len(channels_list)}")

        # Get message count
        while True:
            try:
                message_count = int(input("Messages per channel: ").strip())
                if message_count > 0:
                    break
                else:
                    print("Please enter a positive number.")
            except ValueError:
                print("Please enter a valid number.")

        # Choose format
        print("\n📊 Output Format:")
        print("1. Normal format (basic info + source)")
        print("2. Enhanced format (parsed locations + events + source)")

        while True:
            format_choice = input("Select format (1 or 2): ").strip()
            if format_choice in ["1", "2"]:
                enhanced_format = format_choice == "2"
                break
            else:
                print("Please enter 1 or 2.")

        # Collect messages
        messages = await collector.collect_from_multiple_channels(channels_list, message_count, enhanced_format)

        if messages:
            # Display sample
            collector.print_sample_messages(messages)

            # Save to CSV
            save_csv = input("\n💾 Save to CSV? (y/n): ").strip().lower()
            if save_csv in ["y", "yes"]:
                collector.save_to_csv(messages)

    except KeyboardInterrupt:
        print("\n⏹️ Collection interrupted by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        await collector.close()
        print("\n👋 Multi-channel collection completed!")


def get_session_file(session_path: str = "telegram_session.session"):
    secret_names = [
        "telegramSessionPart1",
        "telegramSessionPart2",
    ]
    full_bytes = b""

    for name in secret_names:
        part = get_secret(name)
        full_bytes += base64.b64decode(part)
        print(f"Retrieved secret: {name}")

    with open(session_path, "wb") as f:
        f.write(full_bytes)

    print(f"✅ Session file reconstructed at: {session_path}")
    return session_path  # return the file path


if __name__ == "__main__":
    asyncio.run(main())
