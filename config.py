import os
from dotenv import load_dotenv

load_dotenv()

# المفاتيح الأساسية
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# إعدادات الصور
MAX_IMAGE_SIZE = 50 * 1024 * 1024  # 50 ميجابايت
SUPPORTED_FORMATS = ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'tiff']

# إعدادات OCR - EasyOCR يدعم 80+ لغة
OCR_LANGUAGES = ['ko', 'en', 'ja', 'zh-cn', 'zh-tw', 'th', 'vi', 'ar']  # أضف ما تشاء
