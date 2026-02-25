import discord
from discord.ext import commands
import logging
from datetime import datetime
from config import DISCORD_TOKEN, MAX_IMAGE_SIZE, SUPPORTED_FORMATS
from image_processor import ImageProcessor
from ocr_engine import SuperOCREngine
from translator_engine import SuperTranslator
import aiohttp
import io

logger = logging.getLogger(__name__)

class LegendaryManhwaBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.messages = True
        
        super().__init__(command_prefix='!', intents=intents)
        
        self.ocr_engine = SuperOCREngine()
        self.translator = SuperTranslator()
        self.start_time = datetime.now()
        self.processed_count = 0
        
    async def setup_hook(self):
        logger.info("🚀 جاري تجهيز البوت الأسطوري...")
        await self.add_commands()
        
    async def add_commands(self):
        
        @self.command(name='help', aliases=['h', 'مساعدة'])
        async def help_command(ctx):
            embed = discord.Embed(
                title="🤖 **البوت الأسطوري لترجمة المانهوا**",
                description="**بوت احترافي لاستخراج وترجمة النصوص من الصور**",
                color=0x9b59b6
            )
            embed.add_field(
                name="📸 **كيفية الاستخدام**",
                value="فقط أرسل أي صورة مانهوا وسأقوم بترجمتها لك!",
                inline=False
            )
            embed.add_field(
                name="🌐 **اللغات المدعومة**",
                value="الكوري، الياباني، الصيني، الإنجليزي، التايلاندي + 80 لغة أخرى",
                inline=False
            )
            embed.add_field(
                name="⚡ **المميزات**",
                value="• OCR محترف\n• ترجمة متعددة المصادر\n• معالجة الصور تلقائياً\n• دعم الصور الكبيرة",
                inline=False
            )
            embed.add_field(
                name="📊 **الأوامر**",
                value="`!help` - هذه المساعدة\n`!stats` - الإحصائيات\n`!langs` - اللغات المدعومة",
                inline=False
            )
            embed.set_footer(text=f"شغال منذ {self.get_uptime()}")
            await ctx.send(embed=embed)
        
        @self.command(name='stats', aliases=['احصائيات'])
        async def stats_command(ctx):
            embed = discord.Embed(
                title="📊 **إحصائيات البوت الأسطوري**",
                color=0x3498db
            )
            embed.add_field(name="⏱️ وقت التشغيل", value=self.get_uptime(), inline=True)
            embed.add_field(name="📸 صور مترجمة", value=str(self.processed_count), inline=True)
            embed.add_field(name="⚙️ الحالة", value="✅ شغال", inline=True)
            await ctx.send(embed=embed)
        
        @self.command(name='langs', aliases=['اللغات'])
        async def langs_command(ctx):
            embed = discord.Embed(
                title="🌐 **اللغات المدعومة**",
                description="""
                • 🇰🇷 كوري
                • 🇯🇵 ياباني
                • 🇨🇳 صيني
                • 🇺🇸 إنجليزي
                • 🇹🇭 تايلاندي
                • 🇻🇳 فيتنامي
                • 🇦🇪 عربي
                • وأكثر من 80 لغة!
                """,
                color=0x2ecc71
            )
            await ctx.send(embed=embed)
    
    async def on_ready(self):
        logger.info(f'✅ البوت الأسطوري شغال! {self.user.name}')
        logger.info(f'🆔 ID: {self.user.id}')
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="المانهوا | !help"
            )
        )
    
    async def on_message(self, message):
        if message.author == self.user:
            return
        
        await self.process_commands(message)
        
        if message.attachments:
            for attachment in message.attachments:
                await self.process_image(message, attachment)
    
    async def download_image(self, url):
        """تحميل الصورة من الرابط"""
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.read()
        return None
    
    async def process_image(self, message, attachment):
        try:
            # التحقق من الصيغة
            ext = attachment.filename.lower().split('.')[-1]
            if ext not in SUPPORTED_FORMATS:
                await message.channel.send(f"❌ الصيغة `{ext}` غير مدعومة!")
                return
            
            # رسالة التقدم
            status_msg = await message.channel.send("🔄 **جاري تحميل الصورة...**")
            
            # تحميل الصورة
            image_bytes = await self.download_image(attachment.url)
            if not image_bytes:
                await status_msg.edit(content="❌ فشل تحميل الصورة")
                return
            
            await status_msg.edit(content="🔍 **جاري استخراج النصوص...**")
            
            # استخراج النص
            extracted_text = await self.ocr_engine.extract_text(image_bytes)
            if not extracted_text:
                await status_msg.edit(content="❌ لم يتم العثور على نصوص في الصورة")
                return
            
            await status_msg.edit(content="🌐 **جاري الترجمة إلى العربية...**")
            
            # الترجمة
            translated_text = self.translator.translate(extracted_text)
            if not translated_text:
                await status_msg.edit(content="❌ فشلت الترجمة")
                return
            
            # إرسال النتيجة
            self.processed_count += 1
            
            embed = discord.Embed(
                title="📖 **الترجمة الأسطورية**",
                description=translated_text[:2000],
                color=0x9b59b6
            )
            embed.add_field(
                name="📊 معلومات",
                value=f"• حجم الصورة: {len(image_bytes)/1024/1024:.1f} MB\n• عدد الأحرف: {len(extracted_text)}",
                inline=False
            )
            embed.set_footer(text=f"تمت الترجمة بواسطة {self.user.name}")
            
            await status_msg.delete()
            await message.channel.send(embed=embed)
            
            # إرسال النص الأصلي للتوثيق (اختياري)
            if len(extracted_text) < 500:
                await message.channel.send(f"**النص الأصلي:**\n```{extracted_text[:500]}```")
            
        except Exception as e:
            logger.error(f"خطأ في معالجة الصورة: {e}")
            await message.channel.send(f"❌ حدث خطأ: {str(e)[:100]}")
    
    def get_uptime(self):
        delta = datetime.now() - self.start_time
        hours = delta.total_seconds() // 3600
        minutes = (delta.total_seconds() % 3600) // 60
        return f"{int(hours)} ساعة {int(minutes)} دقيقة"
    
    async def close(self):
        logger.info("🔄 جاري إغلاق البوت...")
        await super().close()
