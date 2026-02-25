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
            # تحويل الصورة لـ base64
            encoded = base64.b64encode(image_bytes).decode('utf-8')
            
            # البيانات
            data = {
                'apikey': self.api_key,
                'base64Image': f'data:image/png;base64,{encoded}',
                'language': 'kor',          # كوري
                'OCREngine': '2',            # أفضل محرك
                'isOverlayRequired': False,
                'detectOrientation': True
            }
            
            # إرسال الطلب
            async with aiohttp.ClientSession() as session:
                async with session.post(self.url, data=data) as resp:
                    result = await resp.json()
                    
                    if result.get('IsErroredOnProcessing'):
                        logger.error(f"OCR خطأ: {result.get('ErrorMessage')}")
                        return None
                    
                    # استخراج النص
                    text = ""
                    for parsed in result.get('ParsedResults', []):
                        text += parsed.get('ParsedText', '')
                    
                    return text.strip() if text else None
                    
        except Exception as e:
            logger.error(f"OCR Error: {e}")
            return None
