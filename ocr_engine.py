import aiohttp
import base64
import logging
from config import OCR_API_KEY
from PIL import Image
import io
import math
import asyncio

logger = logging.getLogger(__name__)

class OCREngine:
    def __init__(self):
        self.api_key = OCR_API_KEY
        self.url = "https://api.ocr.space/parse/image"
        self.max_size_kb = 900  # أقل من 1 ميجا لكل جزء
        
    def split_image(self, image_bytes):
        """تقسيم الصورة الكبيرة إلى أجزاء"""
        try:
            # فتح الصورة
            img = Image.open(io.BytesIO(image_bytes))
            width, height = img.size
            
            logger.info(f"📏 أبعاد الصورة: {width}x{height}")
            
            # لو الصورة صغيرة، رجعها زي ما هي
            if height <= 3000 and len(image_bytes) < 1.5 * 1024 * 1024:
                return [(img, 0, height)]
            
            # حساب عدد الأجزاء (كل جزء 2000 بكسل ارتفاع)
            part_height = 2000
            num_parts = math.ceil(height / part_height)
            
            parts = []
            logger.info(f"📦 تقسيم الصورة إلى {num_parts} أجزاء")
            
            for i in range(num_parts):
                y_start = i * part_height
                y_end = min((i + 1) * part_height, height)
                
                # قص الجزء
                part = img.crop((0, y_start, width, y_end))
                parts.append((part, y_start, y_end))
            
            return parts
            
        except Exception as e:
            logger.error(f"خطأ في التقسيم: {e}")
            return []
    
    def compress_part(self, image):
        """ضغط جزء واحد"""
        try:
            # تحويل إلى RGB
            if image.mode == 'RGBA':
                rgb = Image.new('RGB', image.size, (255, 255, 255))
                rgb.paste(image, mask=image.split()[3])
                image = rgb
            
            # ضغط الجودة
            quality = 85
            output = io.BytesIO()
            
            while True:
                output.seek(0)
                output.truncate()
                image.save(output, format='JPEG', quality=quality)
                size_kb = output.tell() / 1024
                
                if size_kb <= self.max_size_kb or quality <= 30:
                    break
                    
                quality -= 10
            
            logger.info(f"📦 حجم الجزء بعد الضغط: {size_kb:.0f}KB")
            return output.getvalue(), size_kb
            
        except Exception as e:
            logger.error(f"خطأ في الضغط: {e}")
            return None, 0
    
    async def extract_part(self, part_bytes, part_num, total_parts):
        """استخراج النص من جزء واحد"""
        try:
            encoded = base64.b64encode(part_bytes).decode('utf-8')
            
            # ✅ اللغات الصحيحة لـ OCR.Space
            data = {
                'apikey': self.api_key,
                'base64Image': f'data:image/jpeg;base64,{encoded}',
                'language': 'kor,ara,eng,jpn,chs',  # chs = صيني مبسط
                'OCREngine': '2',
                'isOverlayRequired': False,
                'detectOrientation': True,
                'scale': True,
                'filetype': 'JPG'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.url, data=data, timeout=60) as resp:
                    result = await resp.json()
                    
                    if result.get('IsErroredOnProcessing'):
                        error_msg = result.get('ErrorMessage', '')
                        logger.error(f"الجزء {part_num} خطأ: {error_msg}")
                        return None
                    
                    text = ""
                    for parsed in result.get('ParsedResults', []):
                        text += parsed.get('ParsedText', '')
                    
                    if text:
                        lines = [line.strip() for line in text.split('\n') if line.strip()]
                        clean_text = '\n'.join(lines)
                        logger.info(f"✅ الجزء {part_num}/{total_parts}: {len(clean_text)} حرف")
                        return clean_text
                    
                    return None
                    
        except Exception as e:
            logger.error(f"الجزء {part_num} خطأ: {e}")
            return None
    
    async def extract_text(self, image_bytes):
        try:
            # تقسيم الصورة
            parts = self.split_image(image_bytes)
            
            if not parts:
                return None
            
            # لو جزء واحد فقط
            if len(parts) == 1:
                part_bytes, size = self.compress_part(parts[0][0])
                if part_bytes:
                    return await self.extract_part(part_bytes, 1, 1)
            
            # استخراج النص من كل جزء
            all_text = []
            for i, (part, y_start, y_end) in enumerate(parts, 1):
                logger.info(f"🔄 معالجة الجزء {i}/{len(parts)}")
                
                # ضغط الجزء
                part_bytes, size_kb = self.compress_part(part)
                if not part_bytes:
                    continue
                
                # استخراج النص
                text = await self.extract_part(part_bytes, i, len(parts))
                if text:
                    all_text.append(text)
                
                # انتظار بين الأجزاء
                await asyncio.sleep(1)
            
            # دمج النصوص
            if all_text:
                final_text = '\n\n---\n\n'.join(all_text)  # فصل بين الأجزاء
                logger.info(f"✅ تم استخراج {len(final_text)} حرف من {len(parts)} أجزاء")
                return final_text
            
            return None
            
        except Exception as e:
            logger.error(f"OCR خطأ: {e}")
            return None
