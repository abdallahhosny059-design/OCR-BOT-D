import easyocr
import logging
from image_processor import ImageProcessor
import io
from PIL import Image

logger = logging.getLogger(__name__)

class SuperOCREngine:
    """محرك OCR متطور باستخدام EasyOCR (يدعم 80+ لغة)"""
    
    _instance = None
    _reader = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._reader is None:
            logger.info("جاري تحميل EasyOCR (قد يستغرق دقيقة في أول مرة)...")
            # قم بتعديل اللغات حسب احتياجك
            self._reader = easyocr.Reader(
                ['ko', 'en', 'ja', 'zh-cn', 'th'],  # الكوري، الإنجليزي، الياباني، الصيني، التايلاندي
                gpu=False,
                model_storage_directory='/tmp/easyocr',
                download_enabled=True
            )
            logger.info("✅ تم تحميل EasyOCR بنجاح")
    
    async def extract_text(self, image_bytes):
        """استخراج النص من الصورة بدقة عالية"""
        try:
            # تحسين الصورة أولاً
            processed_image = ImageProcessor.preprocess_image(image_bytes)
            
            # تحويل البايتات إلى صورة PIL
            image = Image.open(io.BytesIO(processed_image))
            
            # استخراج النص
            result = self._reader.readtext(
                np.array(image),
                paragraph=True,
                width_ths=0.7,
                height_ths=0.7,
                decoder='greedy'
            )
            
            # تجميع النص
            text_parts = []
            for detection in result:
                text_parts.append(detection[1])
            
            full_text = ' '.join(text_parts)
            
            if full_text.strip():
                logger.info(f"✅ تم استخراج {len(full_text)} حرف")
                return full_text.strip()
            else:
                logger.warning("لم يتم العثور على نصوص")
                return None
                
        except Exception as e:
            logger.error(f"خطأ في OCR: {e}")
            return None
