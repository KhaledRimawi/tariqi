import asyncio
import threading
from api import start_api_server
from telegram_consumer import EnhancedTelegramMonitor

async def start_polling_telegram_messages():
    """Start polling Telegram messages."""
    monitor = EnhancedTelegramMonitor()
    try:
        success = await monitor.start_polling_telegram_data()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Monitor error: {e}")
        return 1
    

async def main():
    """Main entry point with unified backend management"""
    
    # Default: Start both services
    print("Starting Telegram consumer + API Server...")
    print("-" * 50)
    
    # Start API server in background thread
    start_api_server()
    telegram_thread = threading.Thread(target=start_polling_telegram_messages, daemon =True)
    telegram_thread.start()

if __name__ == "__main__":
    asyncio.run(main())
    print("✅ Backend services started successfully!")