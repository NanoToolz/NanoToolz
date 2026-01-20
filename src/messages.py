"""
Strings and messages for bot
"""

MESSAGES = {
    "en": {
        "welcome": "🛍️ <b>Welcome to NanoToolz!</b>\n\nYour premium digital products store.",
        "help": "📖 <b>Commands:</b>\n/start - Start\n/help - Help\n/shop - Shop\n/profile - Profile",
        "browse_categories": "📚 <b>Browse Categories</b>",
        "select_currency": "💱 <b>Select Currency</b>",
        "daily_spin_claimed": "You already spun today! Try again tomorrow.",
        "daily_spin_result": "🎉 <b>Daily Spin Result!</b>\n\nYou won {reward} {type}!",
        "referral_program": "🎁 <b>Referral Program</b>\n\nEarn 10% on every referral!",
    },
    "ur": {
        "welcome": "🛍️ <b>نینو ٹول ز میں خوش آمدید!</b>\n\nآپ کی پریمیم ڈیجیٹل پروڈکٹس کی دکان۔",
        "help": "📖 <b>کمانڈز:</b>\n/start - شروع\n/help - مدد\n/shop - خریداری\n/profile - پروفائل",
    },
    "hi": {
        "welcome": "🛍️ <b>नैनोटूल्ज़ में स्वागत है!</b>\n\nआपका प्रीमियम डिजिटल उत्पाद स्टोर।",
        "help": "📖 <b>कमांड्स:</b>\n/start - शुरू\n/help - मदद\n/shop - खरीदारी\n/profile - प्रोफ़ाइल",
    }
}

def get_message(key: str, language: str = "en", **kwargs) -> str:
    """Get translated message"""
    msg = MESSAGES.get(language, {}).get(key, MESSAGES["en"].get(key, ""))
    return msg.format(**kwargs) if kwargs else msg
