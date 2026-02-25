import logging
from deep_translator import GoogleTranslator, PapagoTranslator
import asyncio

logger = logging.getLogger(__name__)

class TranslatorEngine:
    def __init__(self):
        # مترجمين متعددين للتبديل التلقائي
        self.translators = {
            'google': GoogleTranslator,
            'papago': PapagoTranslator  # ممتاز للكوري!
        }
        
    def translate(self, text, target='ar'):
        """ترجمة النص باستخدام أفضل مترجم متاح"""
        try:
            if not text or len(text) < 3:
                return None
                
            logger.info(f"جاري ترجمة: {text[:50]}...")
            
            # محاولات الترجمة
            translated = None
            errors = []
            
            # المحاولة 1: Papago (ممتاز للكوري)
            try:
                papago = PapagoTranslator(source='ko', target=target)
                translated = papago.translate(text)
                logger.info("✅ تمت الترجمة باستخدام Papago")
                return translated
            except Exception as e:
                errors.append(f"Papago: {e}")
                logger.warning("Papago فشل، نجرب Google...")
            
            # المحاولة 2: Google (ممتاز كبديل)
            try:
                google = GoogleTranslator(source='auto', target=target)
                translated = google.translate(text)
                logger.info("✅ تمت الترجمة باستخدام Google")
                return translated
            except Exception as e:
                errors.append(f"Google: {e}")
            
            # لو فشل كل شيء
            logger.error(f"فشلت كل محاولات الترجمة: {errors}")
            return None
            
        except Exception as e:
            logger.error(f"خطأ في الترجمة: {e}")
            return None
