#!/usr/bin/env python3
"""
AI Prompt Builder for Palestinian Checkpoint Status
This class intelligently builds prompts with MongoDB context for AI responses
"""

import os
from datetime import datetime, timezone
from typing import Dict, Optional, Tuple

from dotenv import load_dotenv
from flask_pymongo import PyMongo

# Load environment variables
load_dotenv()


class AIPromptBuilder:
    """
    Smart prompt builder that extracts checkpoint information from user queries
    and enriches them with real-time data from MongoDB
    """

    def __init__(self, mongo_instance: PyMongo):
        """
        Initialize with MongoDB connection

        Args:
            mongo_instance (PyMongo): Connected MongoDB instance
        """
        self.mongo = mongo_instance
        self.data_collection = mongo_instance.db[os.getenv("MONGO_COLLECTION_DATA")]

    def extract_checkpoint_from_query(self, user_query: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract checkpoint name from user query using AI-driven text analysis

        Args:
            user_query (str): User's question in Arabic

        Returns:
            Tuple[Optional[str], Optional[str]]: (checkpoint_name, None) - simplified return
        """
        if not user_query:
            return None, None

        query_lower = user_query.lower().strip()

        # Remove common punctuation and question marks
        import re

        query_clean = re.sub(r"[؟?.,!]", "", query_lower)

        # Remove common words to focus on checkpoint name
        words_to_remove = [
            "حاجز",
            "حالة",
            "وضع",
            "ما",
            "كيف",
            "هل",
            "في",
            "من",
            "إلى",
            "على",
            "مفتوح",
            "مغلق",
            "سالك",
            "الحال",
            "الوضع",
            "شو",  # Added "شو" as a question word to be removed
        ]

        # Common greeting words that should be filtered out
        greeting_words = ["مرحبا", "أهلا", "السلام", "مساء", "صباح", "تحية"]

        # Extract potential checkpoint name by removing common words
        words = query_clean.split()
        potential_checkpoint_words = []

        for word in words:
            if word not in words_to_remove and word not in greeting_words and len(word) > 1:
                potential_checkpoint_words.append(word)

        # Join the remaining words as potential checkpoint name
        if potential_checkpoint_words:
            potential_checkpoint = " ".join(potential_checkpoint_words)

            # If the extracted name seems too generic or contains only common words, return None
            if (potential_checkpoint in ["القدس", "رام الله", "نابلس"] and len(potential_checkpoint_words) == 1) or len(
                potential_checkpoint_words
            ) == 0:
                return None, None

            # Filter out common greetings
            if potential_checkpoint in greeting_words:
                return None, None

            return potential_checkpoint, None

        return None, None

    def get_latest_checkpoint_status(self, checkpoint_name: str) -> Optional[Dict]:
        """
        Get the latest status for a specific checkpoint from MongoDB using flexible search

        Args:
            checkpoint_name (str): Name of the checkpoint

        Returns:
            Optional[Dict]: Latest checkpoint data or None
        """
        try:
            # Build flexible query filter using regex for partial matching
            query_filter = {"checkpoint_name": {"$regex": checkpoint_name, "$options": "i"}}

            # Get the latest record
            latest_record = self.data_collection.find_one(query_filter, sort=[("message_date", -1)])

            return latest_record

        except Exception as e:
            print(f"Error fetching checkpoint status: {e}")
            return None

    def format_time_ago_arabic(self, dt) -> str:
        """
        Format datetime as relative time in Arabic
        Equivalent to timeFormat.js formatTimeAgo function
        Args:
            dt: Datetime object or string
        Returns:
            str: Formatted Arabic relative time string
        """
        if not dt:
            return "غير محدد"

        try:
            # Parse datetime string if needed
            if isinstance(dt, str):
                try:
                    dt = datetime.fromisoformat(dt.replace("Z", "+00:00"))
                except (ValueError, AttributeError):
                    return "غير محدد"

            # Get current time in UTC
            now = datetime.now(timezone.utc)
            # Ensure dt is timezone aware
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)

            # Calculate time difference (similar to JavaScript logic)
            diff = now - dt
            diff_seconds = int(diff.total_seconds())

            if diff_seconds < 0:
                return "الآن"

            # Arabic relative time formatting (matching timeFormat.js behavior)
            if diff_seconds < 60:
                return "منذ لحظات"  # More natural than showing exact seconds
            diff_minutes = diff_seconds // 60
            if diff_minutes < 60:
                if diff_minutes == 1:
                    return "منذ دقيقة"
                elif diff_minutes == 2:
                    return "منذ دقيقتين"
                elif diff_minutes <= 10:
                    return f"منذ {diff_minutes} دقائق"
                else:
                    return f"منذ {diff_minutes} دقيقة"
            diff_hours = diff_minutes // 60
            if diff_hours < 24:
                if diff_hours == 1:
                    return "منذ ساعة"
                elif diff_hours == 2:
                    return "منذ ساعتين"
                elif diff_hours <= 10:
                    return f"منذ {diff_hours} ساعات"
                else:
                    return f"منذ {diff_hours} ساعة"
            diff_days = diff_hours // 24
            if diff_days == 1:
                return "منذ يوم"
            elif diff_days == 2:
                return "منذ يومين"
            elif diff_days <= 10:
                return f"منذ {diff_days} أيام"
            else:
                return f"منذ {diff_days} يوم"

        except Exception as e:
            print(f"Error formatting relative time: {e}")
            return "غير محدد"

    def format_datetime_arabic(self, dt) -> str:
        """
        Format datetime in Arabic-friendly format

        Args:
            dt: Datetime object or string

        Returns:
            str: Formatted Arabic time string
        """
        if not dt:
            return "غير محدد"

        # If it's a string, try to parse it or return as is
        if isinstance(dt, str):
            return dt

        # If it's a datetime object, format it
        try:
            # Format time in 24-hour format
            time_str = dt.strftime("%H:%M:%S")
            date_str = dt.strftime("%Y-%m-%d")

            # Determine if AM or PM
            hour = dt.hour
            if hour < 12:
                period = "صباحاً"
            else:
                period = "مساءً"

            return f"{time_str} {period} بتاريخ {date_str}"
        except Exception as e:
            print(f"Error formatting datetime: {e}")
            return str(dt)

    def build_smart_prompt(self, user_query: str) -> str:
        """
        Build an intelligent prompt with checkpoint context for AI

        Args:
            user_query (str): Original user query

        Returns:
            str: Enhanced prompt with context for AI model
        """
        # Extract checkpoint information
        checkpoint_name, _ = self.extract_checkpoint_from_query(user_query)

        if not checkpoint_name:
            # If the user query is not asking about a specific checkpoint, return a
            # general assistant prompt so the model can handle small-talk, insults,
            # and other non-checkpoint interactions in Arabic.
            return f"""
أنت مساعد ذكي ومتعدد الاستخدامات ومتحدث بالعربية.
سؤال المستخدم: "{user_query}"

ملاحظة مهمة: هذا الاستدعاء مخصَّص للمحادثات العامة (غير المتعلقة بأسماء الحواجز).
أجب باللغة العربية باختصار وبأدب. إذا كان المستخدم مهينًا أو يستخدم ألفاظًا جارحة،
فرد بلطف وحافظ على المهنية (مثال: "أنا هنا للمساعدة، كيف أستطيع مساعدتك؟")،
ولا ترد بالإهانات.

إذا كان السؤال عامًا (معلومات، محادثة، نصيحة) فقم بالإجابة مباشرة ومفيدة.
إذا بدا من السياق أن المستخدم يريد معلومات عن حاجز لكنه لم يذكر اسمًا واضحًا،
اطلب توضيحًا بسيطًا مع أمثلة لأسماء حواجز معروفة: قلنديا، عين سينيا، عطارة، دير استيا، العروب، الجلمة.

تأكد من الرد باللغة العربية فقط.
            """.strip()

        # Get latest checkpoint status
        latest_status = self.get_latest_checkpoint_status(checkpoint_name)

        if not latest_status:
            return f"""
أنت مساعد ذكي متخصص في حالة الحواجز والطرق في فلسطين.

سؤال المستخدم: "{user_query}"

الحاجز المطلوب: {checkpoint_name}

لا توجد معلومات حديثة متوفرة عن حالة حاجز {checkpoint_name}.
يرجى إعلام المستخدم بأنه لا توجد بيانات حديثة متاحة وأنه يمكن المحاولة لاحقاً.

تأكد من الرد باللغة العربية فقط.
            """.strip()

        # Format the latest status information
        status = latest_status.get("status", "غير محدد")
        direction = latest_status.get("direction", "غير محدد")
        message_date = latest_status.get("message_date")
        checkpoint_name_from_db = latest_status.get("checkpoint_name", checkpoint_name)

        # Format time using relative time (منذ X دقيقة/ساعة)
        time_str = self.format_time_ago_arabic(message_date) if message_date else "غير محدد"

        # Build enhanced prompt with context
        enhanced_prompt = f"""
أنت مساعد ذكي متخصص في حالة الحواجز والطرق في فلسطين.

سؤال المستخدم: "{user_query}"
معلومات الحاجز من قاعدة البيانات:
- اسم الحاجز: {checkpoint_name_from_db}
- المدينة: {latest_status.get("city_name", "غير محددة")}
- الحالة: {status}
- الاتجاه: {direction}
- آخر تحديث: {time_str}

        🚨 تعليمات إجبارية - اتبعها حرفياً:

أجب بهذا النص بالضبط حسب الاتجاه:

إذا كان الاتجاه "الاتجاهين" أو "اتجاهين" أو "كلا الاتجاهين":
"حاجز {checkpoint_name_from_db} {status} بالاتجاهين {time_str}"

إذا كان الاتجاه "الدخول" أو "داخل" أو "الداخل" أو "دخول":
"حاجز {checkpoint_name_from_db} {status} للدخول {time_str}"

إذا كان الاتجاه "الخروج" أو "خارج" أو "الخارج" أو "خروج":
"حاجز {checkpoint_name_from_db} {status} للخروج {time_str}"

إذا كان الاتجاه غير محدد أو أي شيء آخر:
"حاجز {checkpoint_name_from_db} {status} {time_str}"مهم:
- استخدم "{time_str}" بالضبط كما هو
- لا تغيير النص أعلاه

✅ مطلوب بالضبط:
{time_str}

🔥 استخدم النص المناسب حسب الاتجاه وضع {time_str} بالضبط!
        """.strip()

        return enhanced_prompt

    def is_checkpoint_query(self, user_query: str) -> bool:
        """
        Check if the user query is asking about checkpoint status

        Args:
            user_query (str): User query

        Returns:
            bool: True if it's a checkpoint-related query
        """
        if not user_query:
            return False

        query_lower = user_query.lower()

        # Keywords that indicate checkpoint queries
        checkpoint_keywords = ["حاجز", "حالة", "وضع", "مفتوح", "مغلق", "سالك", "ازمة", "طريق", "عبور", "مرور", "تفتيش"]

        # Check if query contains checkpoint keywords
        has_keywords = any(keyword in query_lower for keyword in checkpoint_keywords)

        # Check if query mentions a potential checkpoint (simplified check)
        checkpoint_name, _ = self.extract_checkpoint_from_query(user_query)
        has_checkpoint = checkpoint_name is not None

        # Additional check: exclude obvious non-checkpoint queries
        greeting_patterns = ["مرحبا", "أهلا", "السلام عليكم", "كيف الحال", "كيف حالك"]
        is_greeting = any(pattern in query_lower for pattern in greeting_patterns)

        return (has_keywords or has_checkpoint) and not is_greeting

    def post_process_response(self, ai_response: str, user_query: str) -> str:
        """
        Post-process AI response to handle time conversion and direction formatting
        This is a fallback for responses that don't follow the TIMESTAMP pattern

        Args:
            ai_response (str): Original AI response
            user_query (str): Original user query

        Returns:
            str: Processed response with proper time formatting and direction
        """

        # Extract checkpoint information
        checkpoint_name, _ = self.extract_checkpoint_from_query(user_query)

        if not checkpoint_name:
            return ai_response

        # Get latest checkpoint status
        latest_status = self.get_latest_checkpoint_status(checkpoint_name)

        if not latest_status:
            return ai_response

        status = latest_status.get("status", "غير محدد")
        direction = latest_status.get("direction", "غير محدد")
        message_date = latest_status.get("message_date")
        checkpoint_name_from_db = latest_status.get("checkpoint_name", checkpoint_name)

        # Format time for relative time pattern
        time_str = self.format_time_ago_arabic(message_date) if message_date else "غير محدد"

        # Check if response already has relative time pattern
        if "منذ" in ai_response:
            return ai_response

        # Build proper response based on direction
        direction_lower = direction.lower()

        if direction_lower in ["الاتجاهين", "اتجاهين", "كلا الاتجاهين"]:
            processed_response = f"حاجز {checkpoint_name_from_db} {status} بالاتجاهين {time_str}"
        elif direction_lower in ["الدخول", "داخل", "الداخل", "دخول"]:
            processed_response = f"حاجز {checkpoint_name_from_db} {status} للدخول {time_str}"
        elif direction_lower in ["الخروج", "خارج", "الخارج", "خروج"]:
            processed_response = f"حاجز {checkpoint_name_from_db} {status} للخروج {time_str}"
        else:
            processed_response = f"حاجز {checkpoint_name_from_db} {status} {time_str}"

        return processed_response
