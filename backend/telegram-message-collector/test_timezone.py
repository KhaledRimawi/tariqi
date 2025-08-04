#!/usr/bin/env python3
"""
Test script to check timezone conversion
"""

import pytz
from datetime import datetime

def test_timezone():
    """Test timezone conversion"""
    print("🕘 اختبار المناطق الزمنية")
    print("=" * 40)
    
    # الوقت الحالي
    utc_now = datetime.now(pytz.UTC)
    print(f"🌍 التوقيت العالمي (UTC): {utc_now.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # تحويل لتوقيت فلسطين
    palestine_tz = pytz.timezone('Asia/Jerusalem')
    palestine_time = utc_now.astimezone(palestine_tz)
    print(f"🇵🇸 توقيت فلسطين/القدس: {palestine_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # تحويل لتوقيت الأردن (بديل)
    jordan_tz = pytz.timezone('Asia/Amman')
    jordan_time = utc_now.astimezone(jordan_tz)
    print(f"🇯🇴 توقيت عمان: {jordan_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n📋 المناطق الزمنية المتاحة في المنطقة:")
    middle_east_timezones = [
        'Asia/Jerusalem',
        'Asia/Gaza', 
        'Asia/Hebron',
        'Asia/Amman',
        'Asia/Damascus',
        'Asia/Beirut'
    ]
    
    for tz_name in middle_east_timezones:
        try:
            tz = pytz.timezone(tz_name)
            local_time = utc_now.astimezone(tz)
            print(f"  {tz_name}: {local_time.strftime('%H:%M:%S')}")
        except:
            print(f"  {tz_name}: غير متاح")

if __name__ == "__main__":
    test_timezone()
