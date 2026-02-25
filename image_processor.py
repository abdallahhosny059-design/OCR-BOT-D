import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)

class ImageProcessor:
    """معالج صور متطور جداً لتحسين OCR"""
    
    @staticmethod
    def preprocess_for_ocr(image_bytes):
        """سلسلة معالجات متعددة لضمان أفضل استخراج"""
        try:
            # قراءة الصورة
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                return image_bytes
            
            # 1. تحويل إلى grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # 2. تحسين التباين باستخدام CLAHE
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(gray)
            
            # 3. إزالة التشويش مع الحفاظ على الحواف
            denoised = cv2.bilateralFilter(enhanced, 9, 75, 75)
            
            # 4. تكبير الصورة إذا كانت صغيرة جداً (تحسين دقة النص الصغير)
            height, width = denoised.shape
            if height < 800 or width < 800:
                scale = max(2.0, 1200 / min(height, width))
                new_size = (int(width * scale), int(height * scale))
                denoised = cv2.resize(denoised, new_size, interpolation=cv2.INTER_CUBIC)
            
            # 5. تحويل إلى ثنائي باستخدام Adaptive Threshold
            binary = cv2.adaptiveThreshold(denoised, 255, 
                                           cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                           cv2.THRESH_BINARY, 11, 2)
            
            # 6. إزالة النقاط الصغيرة (salt & pepper)
            kernel = np.ones((1,1), np.uint8)
            cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            
            # تحويل مرة أخرى إلى بايتات
            success, buffer = cv2.imencode('.png', cleaned)
            if success:
                return buffer.tobytes()
            
            return image_bytes
            
        except Exception as e:
            logger.error(f"خطأ في معالجة الصورة: {e}")
            return image_bytes
