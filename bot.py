import discord
from discord.ext import commands
import logging
from datetime import datetime
import aiohttp
from config import DISCORD_TOKEN, SUPPORTED_FORMATS
from ocr_engine import OCREngine
from translator_engine import TranslatorEngine

logger = logging.getLogger(__name__)

class ManhwaBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        
        super().__init__(command_prefix='!', intents=intents)
        
        self.ocr = OCREngine()
        self.translator = TranslatorEngine()
        self.start_time = datetime.now()
        self.count = 0
    
    async def on_ready(self):
        logger.info(f'✅ البوت شغال! {self.user.name}')
        await self.change_presence(activity=discord.Game(name="📖 أرسل صورة مانهوا"))
    
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
            # تحقق الصيغة
            ext = attachment.filename.lower().split('.')[-1]
            if ext not in SUPPORTED_FORMATS:
                await message.channel.send(f"❌ الصيغة {ext} ممنوعة")
                return
            
            msg = await message.channel.send("🔄 **جاري التحميل...**")
            
            # تحميل الصورة
            img_bytes = await self.download_image(attachment.url)
            if not img_bytes:
                await msg.edit(content="❌ فشل التحميل")
                return
            
            await msg.edit(content="🔍 **OCR.Space بتفحص الصورة...**")
            
            # استخراج النص
            original = await self.ocr.extract_text(img_bytes)
            if not original:
                await msg.edit(content="❌ مفيش نص في الصورة")
                return
            
            await msg.edit(content="🌐 **Papago/Google بيترجموا...**")
            
            # الترجمة
            translated = self.translator.translate(original)
            if not translated:
                await msg.edit(content="❌ الترجمة فشلت")
                return
            
            self.count += 1
            
            # إرسال النتيجة
            embed = discord.Embed(
                title=f"📖 **النتيجة #{self.count}**",
                color=0x00ff00
            )
            
            # النص الأصلي
            if len(original) > 500:
                original = original[:500] + "..."
            embed.add_field(name="📝 المستخرج", value=f"```{original}```", inline=False)
            
            # الترجمة
            if len(translated) > 500:
                translated = translated[:500] + "..."
            embed.add_field(name="🌍 الترجمة", value=translated, inline=False)
            
            await msg.delete()
            await message.channel.send(embed=embed)
            
        except Exception as e:
            await message.channel.send(f"❌ خطأ: {str(e)[:100]}")
    
    @commands.command(name='help')
    async def help_command(self, ctx):
        embed = discord.Embed(
            title="🤖 بوت المانهوا",
            description="أرسل صورة واستخرج النص + الترجمة",
            color=0x9b59b6
        )
        embed.add_field(name="🌐 المحرك", value="OCR.Space + Papago/Google")
        embed.add_field(name="📊 الإحصائيات", value="`!stats`")
        await ctx.send(embed=embed)
    
    @commands.command(name='stats')
    async def stats_command(self, ctx):
        delta = datetime.now() - self.start_time
        hours = delta.total_seconds() // 3600
        minutes = (delta.total_seconds() % 3600) // 60
        
        embed = discord.Embed(title="📊 إحصائيات", color=0x3498db)
        embed.add_field(name="⏱️ الوقت", value=f"{int(hours)}س {int(minutes)}د")
        embed.add_field(name="📸 صور", value=str(self.count))
        await ctx.send(embed=embed)
