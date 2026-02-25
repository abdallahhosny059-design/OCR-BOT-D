import discord
from discord.ext import commands
import logging
from datetime import datetime
from config import MAX_IMAGE_SIZE
from image_handler import ImageHandler
from ocr_engine import OCREngine
from translator_engine import TranslatorEngine

logger = logging.getLogger(__name__)

class ManhwaBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        
        super().__init__(command_prefix='!', intents=intents)
        
        self.image_handler = ImageHandler()
        self.ocr_engine = OCREngine()
        self.translator = TranslatorEngine()
        self.start_time = datetime.now()
    
    async def on_ready(self):
        logger.info(f'✅ البوت شغال! {self.user.name}')
        await self.change_presence(activity=discord.Game(name="📖 بترجمة المانهوا"))
    
    async def on_message(self, message):
        if message.author == self.user:
            return
        
        await self.process_commands(message)
        
        if not message.attachments:
            return
        
        for attachment in message.attachments:
            await self.process_image(message, attachment)
    
    async def process_image(self, message, attachment):
        try:
            # تحقق من الصيغة
            is_valid, ext = self.image_handler.validate_image(attachment.filename)
            if not is_valid:
                await message.channel.send(f"❌ الصيغة {ext} غير مدعومة!")
                return
            
            msg = await message.channel.send("🔄 جاري المعالجة...")
            
            # تحميل الصورة
            image_data, size = await self.image_handler.download_image(attachment.url)
            if not image_data:
                await msg.edit(content=f"❌ فشل تحميل الصورة (أكبر من 50 ميجا)")
                return
            
            await msg.edit(content="📝 جاري استخراج النص...")
            
            # استخراج النص
            text = await self.ocr_engine.extract_text(image_data)
            if not text:
                await msg.edit(content="❌ لم يتم العثور على نص")
                return
            
            await msg.edit(content="🌐 جاري الترجمة...")
            
            # الترجمة
            translated = self.translator.translate(text)
            if not translated:
                await msg.edit(content="❌ فشلت الترجمة")
                return
            
            # إرسال النتيجة
            embed = discord.Embed(
                title="📖 الترجمة",
                description=translated[:1900],
                color=0x00ff00
            )
            
            await msg.delete()
            await message.channel.send(embed=embed)
            
        except Exception as e:
            await message.channel.send(f"❌ خطأ: {str(e)[:100]}")
    
    async def close(self):
        await self.image_handler.close()
        # await super().close()   # 👈 تم تعليق هذا السطر
