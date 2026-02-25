import requests
import logging
import time

logger = logging.getLogger(__name__)

class TranslatorEngine:
    def __init__(self):
        self.session = requests.Session()
        
    def translate(self, text):
        try:
            if not text or len(text) < 3:
                return None
            
            print(f"🔍 ترجمة: {len(text)} حرف")
            
            # تقسيم النص الطويل إلى أجزاء
            max_chunk = 1000
            if len(text) > max_chunk:
                chunks = [text[i:i+max_chunk] for i in range(0, len(text), max_chunk)]
                translated_chunks = []
                
                for i, chunk in enumerate(chunks):
                    print(f"📦 ترجمة الجزء {i+1}/{len(chunks)}")
                    translated = self._translate_chunk(chunk)
                    if translated:
                        translated_chunks.append(translated)
                    time.sleep(0.5)  # انتظار بين الأجزاء
                
                return ' '.join(translated_chunks) if translated_chunks else None
            
            return self._translate_chunk(text)
            
        except Exception as e:
            logger.error(f"خطأ في الترجمة: {e}")
            return None
    
    def _translate_chunk(self, text):
        """ترجمة جزء صغير من النص"""
        try:
            # كشف اللغة أولاً
            lang_url = "https://translate.googleapis.com/translate_a/single"
            lang_params = {
                "client": "gtx",
                "sl": "auto",
                "tl": "en",
                "dt": "t",
                "q": text[:100]  # أول 100 حرف فقط للكشف
            }
            
            lang_response = self.session.get(lang_url, params=lang_params, timeout=10)
            if lang_response.status_code == 200:
                lang_result = lang_response.json()
                detected_lang = lang_result[2]  # اللغة المكتشفة
                print(f"🌐 اللغة المكتشفة: {detected_lang}")
            else:
                detected_lang = "ko"  # افتراضي كوري
            
            # الترجمة إلى العربية
            url = "https://translate.googleapis.com/translate_a/single"
            params = {
                "client": "gtx",
                "sl": detected_lang,
                "tl": "ar",
                "dt": "t",
                "q": text
            }
            
            response = self.session.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                
                # تجميع الترجمة
                translated_parts = []
                for part in result[0]:
                    if part[0]:
                        translated_parts.append(part[0])
                
                translated = ' '.join(translated_parts)
                print(f"✅ تمت ترجمة {len(translated)} حرف")
                return translated
            else:
                print(f"❌ فشل: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ خطأ: {e}")
            return None
