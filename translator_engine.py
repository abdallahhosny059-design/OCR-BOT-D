import logging
from deep_translator import GoogleTranslator, PapagoTranslator
import asyncio

logger = logging.getLogger(__name__)

class SuperTranslator:
    """محرك ترجمة متعدد مع التبديل التلقائي"""
    
    def __init__(self):
        self.translators = {
            'google': GoogleTranslator,
            'papago': PapagoTranslator,  # ممتاز للكوري
        }
        
    def translate(self, text, source='auto', target='ar'):
        """ترجمة النص مع كشف اللغة التلقائي"""
        try:
            if not text or len(text) < 3:
                return None
            
            # محاولة كشف اللغة
            try:
                detector = GoogleTranslator()
                detected = detector.detect(text)
                source_lang = detected[0] if detected else source
                logger.info(f"اللغة المكتشفة: {source_lang}")
            except:
                source_lang = source
            
            logger.info(f"جاري ترجمة {len(text)} حرف...")
            
            # المحاولة الأولى: Papago (إذا كانت اللغة كورية)
            if source_lang == 'ko':
                try:
                    papago = PapagoTranslator(source='ko', target=target)
                    translated = papago.translate(text)
                    if translated:
                        logger.info("✅ ترجمة ناجحة باستخدام Papago")
                        return translated
                except Exception as e:
                    logger.warning(f"Papago فشل: {e}")
            
            # المحاولة الثانية: Google
            try:
                google = GoogleTranslator(source=source_lang, target=target)
                translated = google.translate(text)
                if translated:
                    logger.info("✅ ترجمة ناجحة باستخدام Google")
                    return translated
            except Exception as e:
                logger.warning(f"Google فشل: {e}")
            
            # المحاولة الثالثة: Google تلقائي
            try:
                google = GoogleTranslator(source='auto', target=target)
                translated = google.translate(text)
                if translated:
                    logger.info("✅ ترجمة ناجحة باستخدام Google (تلقائي)")
                    return translated
            except Exception as e:
                logger.error(f"جميع محاولات الترجمة فشلت: {e}")
                return None
                
        except Exception as e:
            logger.error(f"خطأ جسيم في الترجمة: {e}")
            return None
