import base64
import re
from typing import Any, Dict, List, Tuple

from dotenv import load_dotenv
from keyvault_client import get_secret
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.types import Channel, Chat

load_dotenv()


def rebuild_session_file(path: str = "telegram_session.session") -> str:
    parts = ["telegramSessionPart1", "telegramSessionPart2"]
    blob = b"".join(base64.b64decode(get_secret(p)) for p in parts)
    with open(path, "wb") as f:
        f.write(blob)
    return path


class TelegramCheckpointCollector:
    def __init__(self, api_id: int, api_hash: str, phone_number: str) -> None:
        self.client = TelegramClient(rebuild_session_file(), api_id, api_hash)
        self.phone_number = phone_number

        # checkpoint → city
        self._locations: Dict[str, Dict[str, str]] = {
            # Nablus
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
            # Ramallah
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
            # Jerusalem
            "قلنديا": {"city": "القدس"},
            "كفر عقب": {"city": "القدس"},
            "عناتا": {"city": "القدس"},
            "جبع": {"city": "القدس"},
            "الرام": {"city": "القدس"},
            "شعفاط": {"city": "القدس"},
            "العيزرية": {"city": "القدس"},
            "حزما": {"city": "القدس"},
            # Hebron
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
            # Bethlehem
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
            # Salfit
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
            # Qalqilya
            "المدخل الشرقي": {"city": "قلقيلية"},
            "نفق حبلة": {"city": "قلقيلية"},
            "مدخل اماتين": {"city": "قلقيلية"},
            "مدخل جينصافوط": {"city": "قلقيلية"},
            "جسر عزون": {"city": "قلقيلية"},
            "مدخل كفر لاقف": {"city": "قلقيلية"},
            "حجة": {"city": "قلقيلية"},
            "الفندق": {"city": "قلقيلية"},
            "مدخل النبي الياس": {"city": "قلقيلية"},
            # Tulkarm
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
            # Jenin
            "حومش": {"city": "جنين"},
            "الجلمة": {"city": "جنين"},
            "دوتان": {"city": "جنين"},
            "برطعة": {"city": "جنين"},
            # Jericho / Tubas
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

    async def authenticate(self) -> None:
        await self.client.connect()
        if await self.client.is_user_authorized():
            return
        await self.client.send_code_request(self.phone_number)
        code = input("Enter Telegram code: ")
        try:
            await self.client.sign_in(self.phone_number, code)
        except SessionPasswordNeededError:
            pwd = input("Enter Telegram 2FA password: ")
            await self.client.sign_in(password=pwd)

    async def _entity(self, username_or_link: str):
        try:
            ent = await self.client.get_entity(username_or_link)
            return ent if isinstance(ent, (Channel, Chat)) else None
        except Exception:
            return None

    def parse(self, text: str) -> Tuple[str, str, str, str, str]:
        if not text:
            return "غير محدد", "غير محدد", "غير محدد", "غير محدد", ""
        t = text.lower()
        checkpoint, city = "غير محدد", "غير محدد"
        for loc, info in self._locations.items():
            if loc.lower() in t:
                checkpoint, city = loc, info["city"]
                break
        if checkpoint == "غير محدد":
            for loc, info in self._locations.items():
                words = [w for w in loc.lower().split() if len(w) > 2]
                if any(w in t for w in words):
                    checkpoint, city = loc, info["city"]
                    break

        status = "غير محدد"
        if any(w in t for w in ["شو وضع", "كيف", "ايش وضع", "كيف الوضع", "؟"]):
            status = "استفسار"
        elif any(w in t for w in ["مغلق", "مسكر", "اغلاق", "سكر", "مغلقة", "مسكرة", "❌"]):
            status = "إغلاق"
        elif any(w in t for w in ["ازمة", "أزمة", "كثافة سير", "واقف", "خانقة", "طويلة", "🔴"]):
            status = "أزمة"
        elif any(w in t for w in ["سالك", "سالكة", "فاتح", "مفتوح", "بحري", "نضيف", "✅"]):
            status = "سالك"
        elif any(w in t for w in ["حاجز", "تفتيش", "بفتش", "تواجد جيش", "جيش", "حاجز طيار", "وقف"]):
            status = "حاجز/تفتيش"
        elif any(w in t for w in ["حادث", "حريق", "عطلان", "عطلانه"]):
            status = "حادث"
        elif any(w in t for w in ["فتح", "تم فتح"]):
            status = "فتح"

        direction = "غير محدد"
        if any(w in t for w in ["للداخل", "دخول", "داخل", "للدخول", "ل الداخل"]):
            direction = "دخول"
        elif any(w in t for w in ["للخارج", "خروج", "خارج", "للخروج", "ل الخارج"]):
            direction = "خروج"
        elif any(w in t for w in ["بالاتجاهين", "الاتجاهين", "الجهتين", "باتجاهين"]):
            direction = "الاتجاهين"
        elif checkpoint != "غير محدد" and status not in {"غير محدد", "استفسار"}:
            direction = "الاتجاهين"

        cleaned = re.sub(r"[🔴❌✅️🤍🤝⚠️✋]+", "", text)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return checkpoint, city, status, direction, cleaned

    async def collect(self, channel: str, limit: int, enhanced: bool = True) -> List[Dict[str, Any]]:
        ent = await self._entity(channel)
        if not ent:
            return []
        results: List[Dict[str, Any]] = []
        async for msg in self.client.iter_messages(ent, limit=limit):
            text = msg.text or msg.message or ""
            ts = msg.date
            if enhanced:
                checkpoint, city, status, direction, _ = self.parse(text)
                payload = {
                    "message_id": msg.id,
                    "source_channel": channel,
                    "original_message": text or "[Media message]" if msg.media else text,
                    "checkpoint_name": checkpoint,
                    "city_name": city,
                    "status": status,
                    "direction": direction,
                    "message_date": ts,
                }
            else:
                payload = {
                    "message_id": msg.id,
                    "source_channel": channel,
                    "message_text": text or "[Media message]" if msg.media else text,
                    "message_date": ts,
                    "message_type": "media" if msg.media else "text",
                }
            results.append(payload)
        return results

    async def collect_many(self, channels: List[str], per_channel: int, enhanced: bool = True) -> List[Dict[str, Any]]:
        all_msgs: List[Dict[str, Any]] = []
        for ch in channels:
            all_msgs.extend(await self.collect(ch, per_channel, enhanced))
        return sorted(all_msgs, key=lambda x: x["message_date"], reverse=True)

    async def close(self) -> None:
        await self.client.disconnect()
