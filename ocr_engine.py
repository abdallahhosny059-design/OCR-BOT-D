import aiohttp
import base64
import logging
from config import OCR_API_KEY

logger = logging.getLogger(__name__)

class OCREngine:
    def __init__(self):
        self.api_key = OCR_API_KEY
        self.url = "https://api.ocr.space/parse/image"
        
    async def extract_text(self, image_bytes):
        try:
            encoded = base64.b64encode(image_bytes).decode('utf-8')
            
            # استخدام المحرك المتقدم 2 وتفعيل جميع اللغات
            data = {
                'apikey': self.api_key,
                'base64Image': f'data:image/png;base64,{encoded}',
                'language': 'kor,ara,eng,jpn,chi_sim',  # كوري + عربي + إنجليزي + ياباني + صيني
                'OCREngine': '2',                         # أفضل محرك
                'isOverlayRequired': False,
                'detectOrientation': True,
                'scale': True,                            # تكبير الصورة تلقائياً
                'isTable': False,
                'filetype': 'PNG'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.url, data=data, timeout=60) as resp:  # مهلة أطول
                    result = await resp.json()
                    
                    if result.get('IsErroredOnProcessing'):
                        logger.error(f"OCR خطأ: {result.get('ErrorMessage')}")
                        return None
                    
                    # استخراج النص كاملاً
                    text = ""
                    for parsed in result.get('ParsedResults', []):
                        text += parsed.get('ParsedText', '')
                    
                    # تنظيف النص
                    if text:
                        # إزالة الأسطر الفارغة المتعددة
                        lines = [line.strip() for line in text.split('\n') if line.strip()]
                        text = '\n'.join(lines)
                        
                        logger.info(f"✅ تم استخراج {len(text)} حرف")
                        return text
                    else:
                        logger.warning("لم يتم العثور على نص")
                        return None
                    
        except Exception as e:
            logger.error(f"OCR خطأ: {e}")
            return None
