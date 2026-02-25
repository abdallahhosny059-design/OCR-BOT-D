import logging
from deep_translator import GoogleTranslator, PapagoTranslator

logger = logging.getLogger(__name__)

class SuperTranslator:
    def __init__(self):
        self.google = GoogleTranslator
        self.papago = PapagoTranslator
        
    def translate(self, text, target='ar'):
        """ترجمة النص مع كشف اللغة التلقائي"""
        try:
            if not text or len(text) < 3:
                return None
            
            # محاولة كشف اللغة
            source_lang = 'auto'
            try:
                detector = GoogleTranslator(source='auto', target='en')
                detected = detector.detect(text)
                if detected:
                    source_lang = detected[0]
                    logger.info(f"اللغة المكتشفة: {source_lang}")
            except:
                pass
            
            # إذا كانت كورية، استخدم Papago (أفضل للكوري)
            if source_lang == 'ko':
                try:
                    papago = PapagoTranslator(source='ko', target=target)
                    translated = papago.translate(text)
                    if translated:
                        logger.info("✅ ترجمة باستخدام Papago")
                        return translated
                except Exception as e:
                    logger.warning(f"Papago فشل: {e}")
            
            # Google مترجم احتياطي
            try:
                google = GoogleTranslator(source=source_lang, target=target)
                translated = google.translate(text)
                if translated:
                    logger.info("✅ ترجمة باستخدام Google")
                    return translated
            except Exception as e:
                logger.error(f"Google فشل: {e}")
            
            # محاولة أخيرة مع auto
            try:
                google = GoogleTranslator(source='auto', target=target)
                translated = google.translate(text)
                if translated:
                    logger.info("✅ ترجمة باستخدام Google (auto)")
                    return translated
            except Exception as e:
                logger.error(f"جميع المحاولات فشلت: {e}")
                
            return None
            
        except Exception as e:
            logger.error(f"خطأ في الترجمة: {e}")
            return None
