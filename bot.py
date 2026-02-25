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
        await self.change_presence(activity=discord.Game(name="📖 أرسل صورة للترجمة"))
    
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
    
    def split_into_sentences(self, text, max_length=1000):
        """تقسيم النص إلى جمل"""
        # نقاط نهاية الجمل
        delimiters = ['.', '!', '?', '。', '！', '？', '\n']
        
        sentences = []
        current = ""
        
        for char in text:
            current += char
            if char in delimiters and len(current) > 30:
                sentences.append(current.strip())
                current = ""
        
        if current:
            sentences.append(current.strip())
        
        # تقسيم الجمل الطويلة
        final_sentences = []
        for sentence in sentences:
            if len(sentence) > max_length:
                # تقسيم إلى أجزاء أصغر
                words = sentence.split()
                part = ""
                for word in words:
                    if len(part) + len(word) < max_length:
                        part += " " + word
                    else:
                        if part:
                            final_sentences.append(part.strip())
                        part = word
                if part:
                    final_sentences.append(part.strip())
            else:
                final_sentences.append(sentence)
        
        return final_sentences
    
    async def process_image(self, message, attachment):
        try:
            # تحقق الصيغة
            ext = attachment.filename.lower().split('.')[-1]
            if ext not in SUPPORTED_FORMATS:
                await message.channel.send(f"❌ الصيغة `{ext}` غير مدعومة")
                return
            
            msg = await message.channel.send("🔄 **جاري التحميل والمعالجة...**")
            
            # تحميل الصورة
            img_bytes = await self.download_image(attachment.url)
            if not img_bytes:
                await msg.edit(content="❌ فشل التحميل")
                return
            
            await msg.edit(content="🔍 **OCR.Space بتحليل الصورة...**")
            
            # استخراج النص
            original = await self.ocr.extract_text(img_bytes)
            if not original:
                await msg.edit(content="❌ لم يتم العثور على نص")
                return
            
            await msg.edit(content="🌐 **جاري الترجمة (قد تستغرق دقيقة)...**")
            
            # الترجمة
            translated = self.translator.translate(original)
            if not translated:
                await msg.edit(content="❌ فشلت الترجمة")
                return
            
            self.count += 1
            
            await msg.delete()
            
            # تقسيم النصوص إلى جمل
            original_sentences = self.split_into_sentences(original)
            translated_sentences = self.split_into_sentences(translated)
            
            # إرسال كل 5 جمل في رسالة
            for i in range(0, max(len(original_sentences), len(translated_sentences)), 5):
                embed = discord.Embed(
                    title=f"📖 **الجزء {i//5 + 1}**" if i > 0 else f"📖 **الترجمة #{self.count}**",
                    color=0x9b59b6
                )
                
                # النص الأصلي
                orig_part = "\n".join(original_sentences[i:i+5])
                if orig_part:
                    embed.add_field(
                        name="📝 **النص الأصلي**",
                        value=f"```{orig_part[:500]}```",
                        inline=False
                    )
                
                # الترجمة
                trans_part = "\n".join(translated_sentences[i:i+5])
                if trans_part:
                    embed.add_field(
                        name="🌍 **الترجمة**",
                        value=trans_part[:500],
                        inline=False
                    )
                
                await message.channel.send(embed=embed)
            
        except Exception as e:
            await message.channel.send(f"❌ خطأ: {str(e)[:100]}")
    
    @commands.command(name='help', aliases=['مساعدة'])
    async def help_command(self, ctx):
        embed = discord.Embed(
            title="🤖 **بوت الترجمة المتطور**",
            description="**أرسل أي صورة وسأقوم باستخراج النص وترجمته**",
            color=0x00ff00
        )
        embed.add_field(name="🌐 **اللغات المدعومة**", value="كوري • عربي • إنجليزي • ياباني • صيني", inline=False)
        embed.add_field(name="⚡ **المميزات**", value="• استخراج دقيق\n• ترجمة احترافية\n• تقسيم الجمل تلقائياً\n• دعم الصور الطويلة", inline=False)
        embed.add_field(name="📊 **الأوامر**", value="`!stats` - الإحصائيات", inline=True)
        await ctx.send(embed=embed)
    
    @commands.command(name='stats')
    async def stats_command(self, ctx):
        delta = datetime.now() - self.start_time
        hours = delta.total_seconds() // 3600
        minutes = (delta.total_seconds() % 3600) // 60
        
        embed = discord.Embed(title="📊 **الإحصائيات**", color=0x3498db)
        embed.add_field(name="⏱️ **وقت التشغيل**", value=f"{int(hours)}س {int(minutes)}د")
        embed.add_field(name="📸 **صور مترجمة**", value=str(self.count))
        embed.add_field(name="⚙️ **الحالة**", value="✅ شغال")
        await ctx.send(embed=embed)
