import requests
import logging

logger = logging.getLogger(__name__)

class TranslatorEngine:
    def translate(self, text):
        try:
            if not text or len(text) < 3:
                return None
            
            print(f"🔍 بترجم: {text[:50]}...")
            
            # Google Translate API (مجاني 100%)
            url = "https://translate.googleapis.com/translate_a/single"
            params = {
                "client": "gtx",
                "sl": "ko",
                "tl": "ar",
                "dt": "t",
                "q": text
            }
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                translated = result[0][0][0]
                print(f"✅ تمت الترجمة: {translated[:50]}...")
                return translated
            else:
                print(f"❌ فشل: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ خطأ: {e}")
            return None
