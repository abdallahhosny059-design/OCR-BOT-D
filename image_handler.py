import aiohttp
from PIL import Image
from io import BytesIO
import logging
from config import MAX_IMAGE_SIZE, MAX_IMAGE_DIMENSION, SUPPORTED_FORMATS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageHandler:
    def __init__(self):
        self.session = None
        
    async def get_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def download_image(self, url):
        try:
            session = await self.get_session()
            async with session.get(url) as response:
                if response.status != 200:
                    return None, 0
                
                image_data = await response.read()
                size_mb = len(image_data) / (1024 * 1024)
                
                # تحقق من الحجم
                if len(image_data) > MAX_IMAGE_SIZE:
                    logger.warning(f"صورة كبيرة جداً: {size_mb} MB")
                    return None, size_mb
                
                # تحقق من الأبعاد
                img = Image.open(BytesIO(image_data))
                if img.width > MAX_IMAGE_DIMENSION or img.height > MAX_IMAGE_DIMENSION:
                    logger.warning(f"أبعاد كبيرة: {img.width}x{img.height}")
                    # تصغير الصورة
                    img.thumbnail((MAX_IMAGE_DIMENSION, MAX_IMAGE_DIMENSION))
                    output = BytesIO()
                    img.save(output, format='PNG')
                    image_data = output.getvalue()
                
                return image_data, size_mb
                
        except Exception as e:
            logger.error(f"خطأ: {e}")
            return None, 0
    
    def validate_image(self, filename):
        ext = filename.lower().split('.')[-1]
        return ext in SUPPORTED_FORMATS, ext
    
    async def close(self):
        if self.session:
            await self.session.close()