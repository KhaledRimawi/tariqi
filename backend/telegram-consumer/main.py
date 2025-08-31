# main.py
import asyncio
import logging
import os

from dotenv import load_dotenv
from keyvault_client import get_secret
from mongodb import MongoDB
from telegram_collector import TelegramCheckpointCollector

load_dotenv()

logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO),
    format="%(asctime)s | %(levelname)s | %(message)s",
)
log = logging.getLogger("main")

POLL_INTERVAL = int(os.getenv("TELEGRAM_CHECK_INTERVAL", "300"))  # default 5 min


async def collect_once():
    api_id = int(os.getenv("TELEGRAM_API_ID", "0"))
    channels = [c.strip() for c in os.getenv("TELEGRAM_CHANNELS", "").split(",") if c.strip()]
    per_channel = int(os.getenv("TELEGRAM_MESSAGE_LIMIT", "50"))
    if not api_id or not channels or not per_channel:
        raise ValueError("Missing TELEGRAM_API_ID / TELEGRAM_CHANNELS / TELEGRAM_MESSAGE_LIMIT")

    api_hash = get_secret("appHash")
    phone = get_secret("PhoneNumber")

    collector = TelegramCheckpointCollector(api_id, api_hash, phone)
    db = MongoDB()

    await collector.authenticate()
    db.connect()
    try:
        log.info(f"Collecting from {len(channels)} channels, {per_channel} msg/channel")
        msgs = await collector.collect_many(channels, per_channel, enhanced=True)
        saved = db.save_messages(msgs)
        log.info(f"Done. collected={len(msgs)} saved={saved}")
    finally:
        await collector.close()
        db.disconnect()


async def main():
    while True:
        try:
            await collect_once()
        except Exception as e:
            log.error(f"cycle failed: {e}")
        log.info(f"Sleeping {POLL_INTERVAL} seconds ({POLL_INTERVAL//60} min)...")
        await asyncio.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    asyncio.run(main())
