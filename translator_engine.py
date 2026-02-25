import translators as ts
import logging

logger = logging.getLogger(__name__)

class TranslatorEngine:
    def translate(self, text):
        try:
            if not text or len(text) < 3:
                return None
            
            # جرب Papago أولاً (أفضل للكوري)
            try:
                translated = ts.translate_text(
                    text,
                    translator='papago',
                    from_language='ko',
                    to_language='ar'
                )
                if translated:
                    logger.info("✅ Papago")
                    return translated
            except:
                pass
            
            # لو فشل، جرب Google
            try:
                translated = ts.translate_text(
                    text,
                    translator='google',
                    from_language='ko',
                    to_language='ar'
                )
                if translated:
                    logger.info("✅ Google")
                    return translated
            except:
                pass
            
            # محاولة أخيرة مع كشف اللغة
            try:
                translated = ts.translate_text(
                    text,
                    translator='bing',
                    to_language='ar'
                )
                if translated:
                    logger.info("✅ Bing")
                    return translated
            except Exception as e:
                logger.error(f"كل المترجمين فشلوا: {e}")
                
            return None
            
        except Exception as e:
            logger.error(f"ترجمة خطأ: {e}")
            return None
