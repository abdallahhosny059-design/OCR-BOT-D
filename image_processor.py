import cv2
import numpy as np
from PIL import Image
import io
import logging

logger = logging.getLogger(__name__)

class ImageProcessor:
    """معالج صور متطور لتحسين دقة OCR"""
    
    @staticmethod
    def preprocess_image(image_bytes):
        """تحسين الصورة لاستخراج النصوص بدقة عالية"""
        try:
            # تحويل البايتات إلى مصفوفة numpy
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # تحويل إلى تدرج الرمادي
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # زيادة التباين
            gray = cv2.equalizeHist(gray)
            
            # إزالة التشويش
            denoised = cv2.fastNlMeansDenoising(gray, h=30)
            
            # تحويل الصورة إلى ثنائية (أسود وأبيض)
            _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # تكبير النص إذا كان صغيراً
            scale_factor = 2.0
            if img.shape[0] < 1000:
                binary = cv2.resize(binary, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_CUBIC)
            
            # تحويل النتيجة إلى بايتات
            success, encoded_image = cv2.imencode('.png', binary)
            if success:
                return encoded_image.tobytes()
            return image_bytes
            
        except Exception as e:
            logger.error(f"خطأ في معالجة الصورة: {e}")
            return image_bytes
