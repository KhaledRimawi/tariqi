#!/usr/bin/env python3
"""
Enhanced Continuous Telegram Monitor
===================================

Improved version with better error handling, logging, and monitoring capabilities.
"""

import asyncio
import json
import signal
import sys
import time
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from pathlib import Path

# Import our custom modules
from multi_channel_collector import MultiChannelTelegramCollector
from mongodb_handler import MongoDBHandler
from secrets import APP_HASH, PHONE_NUMBER


# Configure logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Create logger
logger = logging.getLogger('TelegramMonitor')
logger.setLevel(logging.INFO)

# Create handlers
file_handler = logging.FileHandler(log_dir / "continuous_monitor.log", encoding='utf-8')
console_handler = logging.StreamHandler()

# Create formatters
file_formatter = logging.Formatter(
    '%(asctime)s | %(levelname)8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
console_formatter = logging.Formatter(
    '%(asctime)s | %(levelname)8s | %(message)s',
    datefmt='%H:%M:%S'
)

# Add formatters to handlers
file_handler.setFormatter(file_formatter)
console_handler.setFormatter(console_formatter)

# Add handlers to logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Load variables from an .env file
load_dotenv()

# Reading variables from the environment
SELF_API_ID = int(os.getenv("TELEGRAM_API_ID"))

SELF_CHANNELS = os.getenv("TELEGRAM_CHANNELS", "")
CHANNEL_LIST = [ch.strip() for ch in SELF_CHANNELS.split(",") if ch.strip()]

SELF_CHECK_INTERVAL = int(os.getenv("TELEGRAM_CHECK_INTERVAL"))
SELF_MESSAGE_LIMIT = int(os.getenv("TELEGRAM_MESSAGE_LIMIT"))       

# Verify that the values exist
if not CHANNEL_LIST or not SELF_CHECK_INTERVAL or not SELF_MESSAGE_LIMIT :
    raise ValueError("❌ CHANNEL LIST or CHECK INTERVAL or MESSAGE LIMIT is missing in .env file")


class EnhancedTelegramMonitor:
    """Enhanced continuous Telegram monitoring system"""
    
    def __init__(self):
        # Telegram API credentials
        self.API_ID = SELF_API_ID
        self.API_HASH = APP_HASH
        self.PHONE_NUMBER = PHONE_NUMBER   
        
        # Monitoring settings
        self.CHECK_INTERVAL = SELF_CHECK_INTERVAL
        self.MESSAGE_LIMIT = SELF_MESSAGE_LIMIT
        
        # Channels to monitor
        self.channels = CHANNEL_LIST
        
        # State management
        self.state_file = "monitor_state.json"
        self.last_message_ids = {}
        self.stats = {
            'start_time': None,
            'total_runs': 0,
            'total_messages': 0,
            'errors': 0,
            'last_run': None,
            'last_error': None
        }
        
        # Runtime variables
        self.running = False
        self.start_time = time.time()
        self.collector = None
        self.mongo_handler = None
        self.initialized = False
        self.cycle_count = 0
        self.last_error = None
        
        # Setup signal handlers
        self.setup_signal_handlers()
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"📡 Received signal {signum}")
            self.stop_monitoring()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def stop_monitoring(self):
        """Stop the monitoring process"""
        logger.info("🛑 Stopping monitor...")
        self.running = False
    
    def load_state(self):
        """Load previous monitoring state"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.last_message_ids = data.get('last_message_ids', {})
                    self.stats.update(data.get('stats', {}))
                    logger.info(f"📂 Loaded state: {len(self.last_message_ids)} channel positions")
            else:
                logger.info("📄 No previous state found, starting fresh")
        except Exception as e:
            logger.error(f"❌ Error loading state: {e}")
    
    def save_state(self):
        """Save current monitoring state"""
        try:
            state = {
                'last_message_ids': self.last_message_ids,
                'stats': self.stats,
                'saved_at': datetime.now().isoformat()
            }
            
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"❌ Error saving state: {e}")
    
    async def initialize_services(self):
        """Initialize Telegram client and MongoDB connection with retry logic"""
        max_retries = 3
        retry_delay = 10
        
        for attempt in range(max_retries):
            try:
                logger.info(f"🔄 Initialization attempt {attempt + 1}/{max_retries}")
                
                # Initialize Telegram collector
                logger.info("📱 Initializing Telegram client...")
                self.collector = MultiChannelTelegramCollector(
                    self.API_ID, 
                    self.API_HASH, 
                    self.PHONE_NUMBER
                )
                
                # Authenticate
                await self.collector.authenticate()
                logger.info("✅ Telegram client authenticated")
                
                # Test Telegram connection
                me = await self.collector.client.get_me()
                logger.info(f"👤 Logged in as: {me.first_name} {me.last_name or ''}")
                
                # Initialize MongoDB
                logger.info("🗄️ Connecting to MongoDB...")
                self.mongo_handler = MongoDBHandler()
                if not self.mongo_handler.connect():
                    raise Exception("MongoDB connection failed")
                
                # Test MongoDB connection
                test_count = self.mongo_handler.collection.count_documents({})
                logger.info(f"✅ MongoDB connected (existing documents: {test_count:,})")
                
                # Verify channel access
                await self.verify_channels()
                
                self.initialized = True
                logger.info("🎉 All services initialized successfully!")
                return True
                
            except Exception as e:
                logger.error(f"❌ Initialization attempt {attempt + 1} failed: {e}")
                self.last_error = str(e)
                
                if attempt < max_retries - 1:
                    logger.info(f"⏳ Retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error("❌ All initialization attempts failed")
                    return False
    
    async def verify_channels(self):
        """Verify access to all channels"""
        logger.info("🔍 Verifying channel access...")
        accessible_channels = []
        
        for channel in self.channels:
            try:
                entity = await self.collector.client.get_entity(channel)
                logger.info(f"✅ {entity.title} - {channel}")
                accessible_channels.append(channel)
            except Exception as e:
                logger.warning(f"⚠️ Limited access to {channel}: {e}")
                # Keep channel in list but note the issue
                accessible_channels.append(channel)
        
        logger.info(f"📊 Channel verification complete: {len(accessible_channels)}/{len(self.channels)} accessible")
    
    async def get_new_messages_from_channel(self, channel: str) -> List[Dict[str, Any]]:
        """Get new messages from a specific channel with enhanced logging"""
        try:
            logger.info(f"📡 Scanning {channel.split('/')[-1]}...")
            
            # Get last processed message ID for this channel
            last_id = self.last_message_ids.get(channel, 0)
            
            # Collect recent messages
            messages = await self.collector.collect_from_single_channel(
                channel, 
                message_limit=self.MESSAGE_LIMIT,
                enhanced_format=True
            )
            
            # Filter for new messages only
            new_messages = [msg for msg in messages if msg.get('message_id', 0) > last_id]
            
            if new_messages:
                # Update last message ID
                max_id = max(msg.get('message_id', 0) for msg in new_messages)
                self.last_message_ids[channel] = max_id
                
                logger.info(f"🆕 Found {len(new_messages)} new messages (last ID: {last_id} → {max_id})")
            else:
                logger.info(f"📭 No new messages (current last ID: {last_id})")
            
            return new_messages
            
        except Exception as e:
            logger.error(f"❌ Error scanning {channel}: {e}")
            self.stats['errors'] += 1
            return []
    
    async def process_monitoring_cycle(self):
        """Process one complete monitoring cycle with enhanced error handling"""
        cycle_start = datetime.now()
        self.cycle_count += 1
        
        logger.info(f"🔄 Cycle #{self.cycle_count} starting at {cycle_start.strftime('%H:%M:%S')}")
        
        all_new_messages = []
        channel_results = {}
        
        try:
            # Check each channel for new messages
            for i, channel in enumerate(self.channels, 1):
                channel_name = channel.split('/')[-1]
                logger.info(f"📡 [{i}/{len(self.channels)}] Checking {channel_name}...")
                
                try:
                    new_messages = await self.get_new_messages_from_channel(channel)
                    all_new_messages.extend(new_messages)
                    channel_results[channel] = len(new_messages)
                    
                    if new_messages:
                        logger.info(f"✨ {channel_name}: {len(new_messages)} new messages")
                    
                except Exception as e:
                    logger.error(f"❌ Error processing {channel_name}: {e}")
                    channel_results[channel] = f"Error: {str(e)[:30]}"
            
            # Save new messages to MongoDB
            if all_new_messages:
                logger.info(f"💾 Saving {len(all_new_messages)} messages to MongoDB...")
                ##-----------------------!!!!!!!!!!!!!-------هنا يتم ربط البنامج بالملف الذي يخزن بالماغو 
                try:
                    success_count = self.mongo_handler.save_messages(all_new_messages)
                    logger.info(f"✅ Successfully saved {success_count} messages")
                    
                    # Display sample messages
                    self.display_sample_messages(all_new_messages[:3])
                    
                except Exception as e:
                    logger.error(f"❌ Error saving to MongoDB: {e}")
                    self.stats['errors'] += 1
            else:
                logger.info("📭 No new messages found across all channels")
            
            # Update statistics
            self.stats['total_runs'] += 1
            self.stats['total_messages'] += len(all_new_messages)
            self.stats['last_run'] = cycle_start.isoformat()
            
            # Save state
            self.save_state()
            
            # Log cycle summary
            cycle_duration = (datetime.now() - cycle_start).total_seconds()
            logger.info(f"🏁 Cycle #{self.cycle_count} completed in {cycle_duration:.1f}s")
            logger.info(f"📊 Results: {channel_results}")
            
        except Exception as e:
            logger.error(f"❌ Error in monitoring cycle: {e}")
            self.stats['errors'] += 1
            self.stats['last_error'] = str(e)
    
    def display_sample_messages(self, messages: List[Dict[str, Any]]):
        """Display sample of new messages"""
        if not messages:
            return
            
        logger.info("📝 Sample messages:")
        logger.info("=" * 60)
        
        for i, msg in enumerate(messages, 1):
            channel_name = msg.get('source_channel', '').split('/')[-1]
            checkpoint = msg.get('checkpoint_name', 'غير محدد')
            status = msg.get('status', 'غير محدد')
            message_preview = msg.get('original_message', '')[:50]
            
            logger.info(f"📧 #{i} | {channel_name} | {checkpoint} | {status}")
            logger.info(f"   💬 {message_preview}{'...' if len(message_preview) >= 50 else ''}")
            logger.info(f"   🆔 ID: {msg.get('message_id')} | 📅 {msg.get('message_date')}")
            
        logger.info("=" * 60)
    
    def display_statistics(self):
        """Display current monitoring statistics"""
        uptime = time.time() - self.start_time
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)
        
        logger.info("📊 Monitor Statistics")
        logger.info("-" * 40)
        logger.info(f"⏱️ Uptime: {hours}h {minutes}m")
        logger.info(f"🔄 Cycles completed: {self.stats['total_runs']}")
        logger.info(f"📨 Total messages collected: {self.stats['total_messages']:,}")
        logger.info(f"❌ Errors encountered: {self.stats['errors']}")
        logger.info(f"📡 Monitoring {len(self.channels)} channels")
        logger.info(f"⏰ Check interval: {self.CHECK_INTERVAL // 60} minutes")
        
        if self.stats.get('last_run'):
            last_run = datetime.fromisoformat(self.stats['last_run'])
            logger.info(f"🕐 Last check: {last_run.strftime('%H:%M:%S')}")
        
        logger.info("-" * 40)
    
    async def check_health(self):
        """Comprehensive health check"""
        try:
            health = {
                "timestamp": datetime.now().isoformat(),
                "uptime_hours": round((time.time() - self.start_time) / 3600, 2),
                "total_cycles": self.cycle_count,
                "is_running": self.running,
                "errors": self.stats['errors'],
                "last_error": self.last_error,
                "memory_usage": self.get_memory_usage(),
                "telegram_status": await self.check_telegram_health(),
                "mongodb_status": self.check_mongodb_health()
            }
            
            logger.info(f"🏥 Health Check: {health}")
            return health
            
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_memory_usage(self):
        """Get current memory usage"""
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            return f"{memory_mb:.1f} MB"
        except:
            return "Unknown"
    
    async def check_telegram_health(self):
        """Check Telegram connection health"""
        try:
            if self.collector and self.collector.client:
                me = await self.collector.client.get_me()
                return f"Connected as {me.first_name}"
            else:
                return "Not connected"
        except Exception as e:
            return f"Error: {str(e)[:30]}"
    
    def check_mongodb_health(self):
        """Check MongoDB connection health"""
        try:
            if self.mongo_handler:
                count = self.mongo_handler.collection.count_documents({})
                return f"Connected ({count:,} docs)"
            else:
                return "Not connected"
        except Exception as e:
            return f"Error: {str(e)[:30]}"
    
    async def start_monitoring(self):
        """Start the enhanced monitoring process"""
        logger.info("🚀 Enhanced Telegram Monitor Starting...")
        logger.info("=" * 60)
        logger.info(f"📅 Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"⏰ Check interval: {self.CHECK_INTERVAL} seconds ({self.CHECK_INTERVAL//60} minutes)")
        logger.info(f"📡 Channels: {len(self.channels)}")
        logger.info(f"📝 Message limit per channel: {self.MESSAGE_LIMIT}")
        logger.info("=" * 60)
        
        # Initialize services
        logger.info("🔧 Initializing services...")
        if not await self.initialize_services():
            logger.error("❌ Failed to initialize services. Exiting.")
            return False
        
        # Load previous state
        self.load_state()
        
        # Set start time if not already set
        if not self.stats.get('start_time'):
            self.stats['start_time'] = datetime.now().isoformat()
        
        self.running = True
        logger.info("✅ Monitor is now running!")
        
        try:
            while self.running:
                # Display current statistics
                self.display_statistics()
                
                # Run health check every 10 cycles
                if self.cycle_count > 0 and self.cycle_count % 10 == 0:
                    await self.check_health()
                
                # Process monitoring cycle
                await self.process_monitoring_cycle()
                
                if not self.running:
                    break
                
                # Calculate next run time
                next_run = datetime.now() + timedelta(seconds=self.CHECK_INTERVAL)
                logger.info(f"😴 Sleeping until {next_run.strftime('%H:%M:%S')} ({self.CHECK_INTERVAL//60} minutes)...")
                
                # Sleep with periodic status updates
                for i in range(self.CHECK_INTERVAL):
                    if not self.running:
                        logger.info("🛑 Shutdown signal received during sleep")
                        break
                    
                    await asyncio.sleep(1)
                    
                    # Status update every 60 seconds
                    remaining = self.CHECK_INTERVAL - i - 1
                    if remaining > 0 and remaining % 60 == 0 and remaining >= 60:
                        logger.info(f"⏳ {remaining//60} minutes remaining until next check...")
                        
        except KeyboardInterrupt:
            logger.info("🛑 Keyboard interrupt received")
        except Exception as e:
            logger.error(f"❌ Critical error in monitoring loop: {e}")
            self.last_error = str(e)
            return False
        finally:
            await self.cleanup()
            logger.info("🏁 Enhanced Monitor stopped gracefully")
            return True
    
    async def cleanup(self):
        """Clean up resources"""
        logger.info("🧹 Cleaning up resources...")
        
        # Save final state
        self.save_state()
        
        # Close Telegram client
        if self.collector and self.collector.client:
            try:
                await self.collector.client.disconnect()
                logger.info("📱 Telegram client disconnected")
            except:
                pass
        
        # Close MongoDB connection
        if self.mongo_handler:
            try:
                self.mongo_handler.disconnect()
                logger.info("🗄️ MongoDB connection closed")
            except:
                pass
        
        logger.info("✅ Cleanup completed")

async def main():
    """Main entry point"""
    monitor = EnhancedTelegramMonitor()
    
    try:
        success = await monitor.start_monitoring()
        return 0 if success else 1
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        return 1

if __name__ == "__main__":
    # Run the monitor
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("🛑 Program interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)
