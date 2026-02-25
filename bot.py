import discord
from discord.ext import commands
import logging
from datetime import datetime
import aiohttp
from config import DISCORD_TOKEN, SUPPORTED_FORMATS
from ocr_engine import SuperOCREngine
from translator_engine import SuperTranslator

logger = logging.getLogger(__name__)

class LegendaryManhwaBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.messages = True
        
        super().__init__(command_prefix='!', intents=intents)
        
        self.ocr = SuperOCREngine()
        self.translator = SuperTranslator()
        self.start_time = datetime.now()
        self.processed_count = 0
    
    async def on_ready(self):
        logger.info(f'✅ البوت الأسطوري شغال! {self.user.name}')
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
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    return await resp.read()
        return None
    
    async def process_image(self, message, attachment):
        try:
            # التحقق من الصيغة
            ext = attachment.filename.lower().split('.')[-1]
            if ext not in SUPPORTED_FORMATS:
                await message.channel.send(f"❌ الصيغة `{ext}` غير مدعومة!")
                return
            
            status = await message.channel.send("🔄 **جاري التحميل والمعالجة...**")
            
            # تحميل الصورة
            img_bytes = await self.download_image(attachment.url)
            if not img_bytes:
                await status.edit(content="❌ فشل تحميل الصورة")
                return
            
            await status.edit(content="🔍 **جاري استخراج النصوص...**")
            
            # استخراج النص
            original_text = await self.ocr.extract_text(img_bytes)
            if not original_text:
                await status.edit(content="❌ لم يتم العثور على نصوص")
                return
            
            await status.edit(content="🌐 **جاري الترجمة...**")
            
            # الترجمة
            translated = self.translator.translate(original_text)
            if not translated:
                await status.edit(content="❌ فشلت الترجمة")
                return
            
            self.processed_count += 1
            
            # إنشاء الـ embed
            embed = discord.Embed(
                title="📖 **نتيجة المعالجة**",
                color=0x9b59b6
            )
            
            # النص الأصلي (مختصر إذا كان طويلاً)
            if len(original_text) > 500:
                original_display = original_text[:500] + "..."
            else:
                original_display = original_text
            
            embed.add_field(
                name="📝 **النص المستخرج**",
                value=f"```{original_display}```",
                inline=False
            )
            
            # الترجمة
            if len(translated) > 500:
                trans_display = translated[:500] + "..."
            else:
                trans_display = translated
            
            embed.add_field(
                name="🌍 **الترجمة إلى العربية**",
                value=trans_display,
                inline=False
            )
            
            embed.set_footer(text=f"تمت المعالجة • الصورة {self.processed_count}")
            
            await status.delete()
            await message.channel.send(embed=embed)
            
        except Exception as e:
            logger.error(f"خطأ: {e}")
            await message.channel.send(f"❌ حدث خطأ: {str(e)[:100]}")
    
    @commands.command(name='help', aliases=['h', 'مساعدة'])
    async def help_command(self, ctx):
        embed = discord.Embed(
            title="🤖 **البوت الأسطوري للترجمة**",
            description="**أرسل أي صورة مانهوا واستخرج النص وترجمته**",
            color=0x00ff00
        )
        embed.add_field(name="🌐 اللغات المدعومة", value="كوري • إنجليزي • صيني", inline=False)
        embed.add_field(name="📊 الإحصائيات", value=f"`!stats`", inline=True)
        embed.add_field(name="⚡ الحالة", value="✅ شغال", inline=True)
        await ctx.send(embed=embed)
    
    @commands.command(name='stats', aliases=['احصائيات'])
    async def stats_command(self, ctx):
        delta = datetime.now() - self.start_time
        hours = delta.total_seconds() // 3600
        minutes = (delta.total_seconds() % 3600) // 60
        
        embed = discord.Embed(title="📊 إحصائيات البوت", color=0x3498db)
        embed.add_field(name="⏱️ وقت التشغيل", value=f"{int(hours)} س {int(minutes)} د")
        embed.add_field(name="📸 صور مترجمة", value=str(self.processed_count))
        await ctx.send(embed=embed)
