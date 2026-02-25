import easyocr
import logging
from image_processor import ImageProcessor
import numpy as np
from PIL import Image
import io

logger = logging.getLogger(__name__)

class SuperOCREngine:
    """محرك OCR متطور باستخدام EasyOCR - يدعم كوري، إنجليزي، صيني"""
    
    _instance = None
    _reader = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._reader is None:
            logger.info("🚀 جاري تحميل نماذج OCR (كوري، إنجليزي، صيني)...")
            # اللغات المطلوبة: كوري، إنجليزي، صيني مبسط
            self._reader = easyocr.Reader(
                ['ko', 'en', 'ch_sim'],
                gpu=False,
                model_storage_directory='/tmp/easyocr',
                download_enabled=True,
                detector=True,
                recognizer=True,
                verbose=False
            )
            logger.info("✅ تم تحميل النماذج بنجاح")
    
    async def extract_text(self, image_bytes):
        """استخراج النص بدقة عالية جداً"""
        try:
            # 1. معالجة الصورة لتحسين الجودة
            processed_bytes = ImageProcessor.preprocess_for_ocr(image_bytes)
            
            # 2. تحويل إلى numpy array
            image = Image.open(io.BytesIO(processed_bytes))
            image_np = np.array(image)
            
            # 3. ضبط إعدادات OCR للحصول على أفضل نتيجة
            result = self._reader.readtext(
                image_np,
                paragraph=True,
                width_ths=0.5,        # تجميع الكلمات المتقاربة
                height_ths=0.5,
                x_ths=0.5,
                y_ths=0.5,
                decoder='beamsearch',  # أفضل دقة (أبطأ قليلاً)
                beamWidth=5,
                batch_size=1,
                workers=1,
                contrast_ths=0.2,
                adjust_contrast=0.5,
                text_threshold=0.7,    # عتبة الثقة
                low_text=0.4,
                link_threshold=0.4,
                canvas_size=2560,
                mag_ratio=1.5,
                slope_ths=0.5
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
