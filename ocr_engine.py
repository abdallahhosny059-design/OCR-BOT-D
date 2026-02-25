import aiohttp
import base64
import logging
from config import OCR_API_KEY, OCR_API_URL, OCR_LANGUAGE

logger = logging.getLogger(__name__)

class OCREngine:
    def __init__(self):
        self.api_key = OCR_API_KEY
        self.api_url = OCR_API_URL
        
    async def extract_text(self, image_data):
        try:
            encoded = base64.b64encode(image_data).decode('utf-8')
            
            data = {
                'apikey': self.api_key,
                'base64Image': f'data:image/png;base64,{encoded}',
                'language': OCR_LANGUAGE,
                'OCREngine': '2'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, data=data) as resp:
                    result = await resp.json()
                    
                    if result.get('IsErroredOnProcessing'):
                        return None
                    
                    text = ""
                    for parsed in result.get('ParsedResults', []):
                        text += parsed.get('ParsedText', '')
                    
                    return text.strip() if text else None
                    
        except Exception as e:
            logger.error(f"OCR Error: {e}")
            return None