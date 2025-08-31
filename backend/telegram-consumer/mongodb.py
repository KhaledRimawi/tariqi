import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional

from dotenv import load_dotenv
from keyvault_client import get_secret
from pymongo import MongoClient

load_dotenv()

_DB = os.getenv("MONGO_DB_NAME")
_COL = os.getenv("MONGO_COLLECTION_DATA")
_SECRET_KEY = os.getenv("MONGO_CONNECTION_STRING_KEY") or "mongodbConnectionString"
if not _DB or not _COL:
    raise ValueError("MONGO_DB_NAME or MONGO_COLLECTION_DATA is missing.")

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def _to_utc(value: Any) -> Optional[datetime]:
    """Convert any datetime or string to UTC.
    If naive -> assume system local time, then convert to UTC."""
    if value is None:
        return None

    if isinstance(value, datetime):
        dt = value
    elif isinstance(value, str):
        s = value.strip()
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        try:
            dt = datetime.fromisoformat(s)
        except Exception:
            try:
                dt = datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
            except Exception:
                return None
    else:
        return None

    if dt.tzinfo is None:
        # Attach system local tz
        local_tz = datetime.now().astimezone().tzinfo
        dt = dt.replace(tzinfo=local_tz)

    return dt.astimezone(timezone.utc)


def _is_noise(text: str) -> bool:
    if not text:
        return True
    t = text.lower().strip()
    if t in {"شكرا", "مرحبا", "اهلا", "تسلم", "يعطيك العافية"}:
        return True
    patterns = [
        "شكرا",
        "شكراً",
        "مرحبا",
        "أهلا",
        "السلام عليكم",
        "مساء الخير",
        "صباح الخير",
        "تحية",
        "بارك الله",
        "الله يعطيك",
        "يا جماعة",
        "ربنا يبارك",
        "🙏",
        "❤️",
    ]
    if any(p in t for p in patterns) and len(t) < 30:
        return True
    non_checkpoint = ["مخارج", "مداخل", "عام", "عمومي", "اعلان", "تنبيه عام"]
    return any(p in t for p in non_checkpoint) and len(t) < 50


class MongoDB:
    def __init__(self) -> None:
        self._conn_str = get_secret(_SECRET_KEY)
        self._client: Optional[MongoClient] = None
        self.collection = None

    def connect(self) -> None:
        # tz_aware=True makes reads return tz-aware datetimes
        self._client = MongoClient(self._conn_str, tz_aware=True)
        self.collection = self._client[_DB][_COL]
        self._client.admin.command("ping")
        logger.info("MongoDB: connected")

    def disconnect(self) -> None:
        if self._client:
            self._client.close()
            logger.info("MongoDB: disconnected")

    def save_messages(self, messages: Iterable[Dict[str, Any]]) -> int:
        msgs = list(messages)
        if not msgs:
            logger.info("MongoDB: nothing to save")
            return 0

        docs: List[Dict[str, Any]] = []
        for m in msgs:
            checkpoint = (m.get("checkpoint_name") or "").strip()
            city = (m.get("city_name") or "").strip()
            status = (m.get("status") or "").strip()
            original = (m.get("original_message") or "").strip()

            if all(x in {"غير محدد", "", None} for x in (checkpoint, city, status)):
                continue
            if _is_noise(original):
                continue

            dt = _to_utc(m.get("message_date")) or datetime.now(timezone.utc)
            docs.append(
                {
                    "message_id": m.get("message_id"),
                    "source_channel": m.get("source_channel"),
                    "original_message": original,
                    "checkpoint_name": checkpoint,
                    "city_name": city,
                    "status": status,
                    "direction": (m.get("direction") or "").strip(),
                    "message_date": dt,  # UTC with tzinfo
                }
            )

        if not docs:
            logger.info("MongoDB: all messages filtered")
            return 0

        self.collection.insert_many(docs, ordered=False)
        logger.info(f"MongoDB: inserted {len(docs)} docs")
        return len(docs)
