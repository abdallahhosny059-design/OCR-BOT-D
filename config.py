import os
from dotenv import load_dotenv

load_dotenv()

# المفاتيح الأساسية
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OCR_API_KEY = os.getenv('OCR_API_KEY')

# إعدادات الصور - صور كبيرة جداً
MAX_IMAGE_SIZE = 50 * 1024 * 1024  # 50 ميجابايت
MAX_IMAGE_DIMENSION = 20000  # 20,000 بكسل
SUPPORTED_FORMATS = ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp']

# إعدادات OCR
OCR_LANGUAGE = os.getenv('OCR_LANGUAGE', 'kor')
OCR_API_URL = 'https://api.ocr.space/parse/image'