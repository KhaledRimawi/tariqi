"""
MongoDB Database Handler for Telegram Message Collector
"""
from pymongo import MongoClient
from dotenv import load_dotenv
from typing import List, Dict, Any
import logging
from appsecrets import MONGO_CONNECTION_STRING
import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# Reading variables from the environment
SELF_DB_NAME = os.getenv("MONGO_DB_NAME")
SELF_COLLECTION_DATA = os.getenv("MONGO_COLLECTION_DATA")

# Verify that the values exist
if not SELF_DB_NAME or not SELF_COLLECTION_DATA :
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
        """Connect to MongoDB"""
        try:
            self.client = MongoClient(self.connection_string)
            self.db = SELF_DB_NAME
            self.collection = SELF_COLLECTION_DATA
            
            # Test connection
            self.client.admin.command('ping')
            logger.info("✅ Successfully connected to MongoDB Atlas")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            return False
    
    def disconnect(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("📝 MongoDB connection closed")
    
    def save_messages(self, messages: List[Dict[str, Any]]) -> bool:
        """
        Save telegram messages to MongoDB
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not messages:
            logger.warning("⚠️ No messages to save")
            return False
        #Array of Objects  
        try:
            # Convert messages to MongoDB format
            mongo_docs = []
            for msg in messages:
                # Map our format to the expected MongoDB format
                doc = {
                    "message_id": msg.get('message_id'),
                    "source_channel": msg.get('source_channel'),
                    "original_message": msg.get('original_message'),
                    "checkpoint_name": msg.get('checkpoint_name'),
                    "city_name": msg.get('city_name'),
                    "status": msg.get('status'),
                    "direction": msg.get('direction'),
                    "message_date": msg.get('message_date')
                    # Removed updatedAt field
                }
                mongo_docs.append(doc)
            
            # Insert into MongoDB
            result = self.collection.insert_many(mongo_docs)
            
            logger.info(f"✅ Successfully inserted {len(result.inserted_ids)} messages into MongoDB")
            logger.info(f"📊 Inserted IDs: {[str(id) for id in result.inserted_ids[:3]]}{'...' if len(result.inserted_ids) > 3 else ''}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save messages to MongoDB: {e}")
            return False
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        try:
            count = self.collection.count_documents({})
            return {
                "total_documents": count,
                "collection_name": f"{SELF_DB_NAME}",
                "database_name": f"{SELF_COLLECTION_DATA}"
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
