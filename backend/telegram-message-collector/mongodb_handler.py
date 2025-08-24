"""
MongoDB Database Handler for Telegram Message Collector
"""

import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict

from dotenv import load_dotenv
from pymongo import MongoClient

from appsecrets import MONGO_CONNECTION_STRING

# Load variables from .env file
load_dotenv()

# Reading variables from the environment
SELF_DB_NAME = os.getenv("MONGO_DB_NAME")
SELF_COLLECTION_DATA = os.getenv("MONGO_COLLECTION_DATA")


def _normalize_dt_utc(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).replace(tzinfo=None) if value.tzinfo else value
    if isinstance(value, str):
        s = value.strip()
        try:
            if s.endswith("Z"):
                s = s[:-1] + "+00:00"
            dt = datetime.fromisoformat(s)
            return dt.astimezone(timezone.utc).replace(tzinfo=None) if dt.tzinfo else dt
        except Exception:
            try:
                return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
            except Exception:
                return None
    return None


# Verify that the values exist
if not SELF_DB_NAME or not SELF_COLLECTION_DATA:
    raise ValueError("❌ SELF_DB_NAME or SELF_COLLECTION_DATA is missing in .env file")


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MongoDBHandler:
    """Handle MongoDB operations for telegram messages"""

    def __init__(self):
        """Initialize MongoDB connection"""
        self.connection_string = MONGO_CONNECTION_STRING
        self.client = None
        self.db = None
        self.collection = None

    def connect(self):
        try:
            self.client = MongoClient(self.connection_string)
            self.db = self.client[os.getenv("MONGO_DB_NAME") or os.getenv("SELF_DB_NAME")]
            self.collection = self.db[os.getenv("MONGO_COLLECTION_DATA") or os.getenv("SELF_COLLECTION_DATA")]
            self.client.admin.command("ping")
            logger.info("✅ Connected to MongoDB.")
            return True
        except Exception as e:
            logger.error(f"❌ MongoDB connection failed: {e}")
            return False

    def disconnect(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("📝 MongoDB connection closed")

    def save_messages(self, messages):
        if not messages:
            logger.warning("⚠️ No messages to save")
            return False
        try:
            mongo_docs = []
            for msg in messages:
                dt = _normalize_dt_utc(msg.get("message_date"))
                if dt is None:
                    from datetime import datetime

                    dt = datetime.utcnow()

                doc = {
                    "message_id": msg.get("message_id"),
                    "source_channel": msg.get("source_channel"),
                    "original_message": msg.get("original_message"),
                    "checkpoint_name": msg.get("checkpoint_name"),
                    "city_name": msg.get("city_name"),
                    "status": msg.get("status"),
                    "direction": msg.get("direction"),
                    "message_date": dt,
                }
                mongo_docs.append(doc)

            result = self.collection.insert_many(mongo_docs)
            logger.info(f"✅ Successfully inserted {len(result.inserted_ids)} documents")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to save messages: {e}")
            return False

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        try:
            count = self.collection.count_documents({})
            return {
                "total_documents": count,
                "collection_name": f"{SELF_COLLECTION_DATA}",
                "database_name": f"{SELF_DB_NAME}",
            }
        except Exception as e:
            logger.error(f"❌ Failed to get collection stats: {e}")
            return {}

    def test_connection(self) -> bool:
        """Test MongoDB connection"""
        try:
            if self.connect():
                stats = self.get_collection_stats()
                logger.info(f"📊 Collection stats: {stats}")
                self.disconnect()
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Connection test failed: {e}")
            return False


# Test the connection if run directly
if __name__ == "__main__":
    handler = MongoDBHandler()
    if handler.test_connection():
        print("✅ MongoDB connection test successful!")
    else:
        print("❌ MongoDB connection test failed!")
