import asyncio
import sys
from threading import Thread

from api import start_api_server
from telegram_consumer import EnhancedTelegramMonitor

# Global stop flag
stop_event = asyncio.Event()


async def start_polling_telegram_messages():
    """Start polling Telegram messages."""
    monitor = EnhancedTelegramMonitor()

    async def monitor_loop():
        await monitor.start_polling_telegram_data()

    task = asyncio.create_task(monitor_loop())

    # Wait until stop_event is set
    await stop_event.wait()
    # Stop the monitor gracefully
    monitor.running = False
    await task


def run_api():
    # Keep your Flask API running in a thread
    start_api_server()  # this blocks the thread, but it's fine in a separate thread


async def main():
    """Main entry point with unified backend management"""

    # Default: Start both services
    print("Starting Telegram consumer + API Server...")
    print("-" * 50)

    # Start Flask API in a non-daemon thread
    api_thread = Thread(target=run_api, daemon=True)
    api_thread.start()

    # Run Telegram consumer with retry loop
    try:
        await start_polling_telegram_messages()
    except KeyboardInterrupt:
        print("CTRL+C pressed, shutting down...")
        stop_event.set()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(" CTRL+C received, shutting down gracefully...")
        sys.exit(0)
    except asyncio.CancelledError:
        # Suppress noisy cancellation trace
        sys.exit(0)
