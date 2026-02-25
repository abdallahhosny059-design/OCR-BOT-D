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
        intents.messages = True
        
        super().__init__(command_prefix='!', intents=intents)
        
        self.ocr = OCREngine()
        self.translator = TranslatorEngine()
        self.start_time = datetime.now()
        self.count = 0
        self.temp_messages = []  # للرسائل المؤقتة
        
    async def on_ready(self):
        logger.info(f'✅ البوت شغال! {self.user.name}')
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
            async with message.channel.typing():
                for attachment in message.attachments:
                    await self.process_image(message, attachment)
    
    async def download_image(self, url):
        """تحميل الصورة مع متابعة الحجم"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        # التحقق من الحجم
                        content_length = resp.headers.get('content-length')
                        if content_length and int(content_length) > 50 * 1024 * 1024:
                            logger.warning("صورة أكبر من 50 ميجا")
                            return None, int(content_length)
                        
                        data = await resp.read()
                        size_mb = len(data) / (1024 * 1024)
                        logger.info(f"📥 تم التحميل: {size_mb:.1f} MB")
                        return data, size_mb
            return None, 0
        except Exception as e:
            logger.error(f"خطأ في التحميل: {e}")
            return None, 0
    
    def split_into_paragraphs(self, text, max_length=1500):
        """تقسيم النص إلى فقرات مترابطة"""
        if not text:
            return []
        
        # تقسيم حسب النقاط الرئيسية
        delimiters = ['\n\n', '\n', '. ', '! ', '? ', '。', '！', '？']
        
        paragraphs = []
        current = ""
        
        for char in text:
            current += char
            if any(current.endswith(d) for d in delimiters) and len(current) > 50:
                if len(current) > max_length:
                    # تقسيم الفقرة الطويلة
                    words = current.split()
                    temp = ""
                    for word in words:
                        if len(temp) + len(word) < max_length:
                            temp += " " + word
                        else:
                            if temp:
                                paragraphs.append(temp.strip())
                            temp = word
                    if temp:
                        paragraphs.append(temp.strip())
                else:
                    paragraphs.append(current.strip())
                current = ""
        
        if current:
            paragraphs.append(current.strip())
        
        return paragraphs
    
    async def process_image(self, message, attachment):
        try:
            # التحقق من الصيغة
            ext = attachment.filename.lower().split('.')[-1]
            if ext not in SUPPORTED_FORMATS:
                await message.channel.send(f"❌ **صيغة غير مدعومة**\nالصيغ المدعومة: {', '.join(SUPPORTED_FORMATS)}")
                return
            
            # رسالة الحالة
            status = await message.channel.send("🔄 **جاري التحميل والمعالجة...**")
            self.temp_messages.append(status)
            
            # تحميل الصورة
            img_bytes, size_mb = await self.download_image(attachment.url)
            if not img_bytes:
                await status.edit(content=f"❌ **فشل التحميل**\nالحجم أكبر من 50 ميجا")
                return
            
            await status.edit(content="🔍 **OCR.Space بتحليل الصورة...**")
            
            # استخراج النص
            original = await self.ocr.extract_text(img_bytes)
            if not original:
                await status.edit(content="❌ **لم يتم العثور على نصوص**\nجرب صورة أوضح أو لغة مختلفة")
                return
            
            await status.edit(content="🌐 **جاري الترجمة (قد تستغرق دقيقة)...**")
            
            # الترجمة
            translated = self.translator.translate(original)
            if not translated:
                await status.edit(content="❌ **فشلت الترجمة**\nالمترجم مش متاح حالياً")
                return
            
            self.count += 1
            
            # حذف رسالة الحالة
            await status.delete()
            if status in self.temp_messages:
                self.temp_messages.remove(status)
            
            # تجهيز الـ Embed الرئيسي
            main_embed = discord.Embed(
                title=f"📖 **الترجمة #{self.count}**",
                description=f"تمت المعالجة بنجاح ✅",
                color=0x9b59b6,
                timestamp=datetime.now()
            )
            
            # معلومات الصورة
            main_embed.add_field(
                name="📊 **معلومات الصورة**",
                value=f"• الحجم: {size_mb:.1f} MB\n• الصيغة: {ext.upper()}",
                inline=True
            )
            
            # إحصائيات النص
            main_embed.add_field(
                name="📝 **إحصائيات النص**",
                value=f"• الأحرف: {len(original):,}\n• الكلمات: {len(original.split()):,}",
                inline=True
            )
            
            main_embed.set_footer(text=f"طلب من {message.author.display_name}", icon_url=message.author.avatar.url if message.author.avatar else None)
            
            await message.channel.send(embed=main_embed)
            
            # تقسيم وعرض النتائج
            original_paras = self.split_into_paragraphs(original)
            translated_paras = self.split_into_paragraphs(translated)
            
            # عرض النص الأصلي والمترجم جنباً إلى جنب
            for i in range(max(len(original_paras), len(translated_paras))):
                embed = discord.Embed(
                    title=f"📑 **الجزء {i+1}**" if i < 5 else f"📑 **تكملة...**",
                    color=0x3498db
                )
                
                # النص الأصلي
                if i < len(original_paras):
                    orig_text = original_paras[i]
                    if len(orig_text) > 500:
                        orig_text = orig_text[:500] + "..."
                    embed.add_field(
                        name="📝 **النص الأصلي**",
                        value=f"```{orig_text}```",
                        inline=False
                    )
                
                # الترجمة
                if i < len(translated_paras):
                    trans_text = translated_paras[i]
                    if len(trans_text) > 500:
                        trans_text = trans_text[:500] + "..."
                    embed.add_field(
                        name="🌍 **الترجمة**",
                        value=trans_text,
                        inline=False
                    )
                
                await message.channel.send(embed=embed)
                
                # وقف بعد 10 أجزاء عشان ما نضربش الـ limit
                if i >= 9:
                    await message.channel.send(f"📌 **... وهناك المزيد** (إجمالي {max(len(original_paras), len(translated_paras))} جزء)")
                    break
            
        except Exception as e:
            logger.error(f"خطأ في المعالجة: {e}")
            error_msg = f"❌ **حدث خطأ غير متوقع**\n```{str(e)[:100]}```"
            
            # محاولة إرسال الخطأ لرسالة الحالة إذا موجودة
            if hasattr(self, 'temp_messages') and self.temp_messages:
                try:
                    await self.temp_messages[-1].edit(content=error_msg)
                except:
                    await message.channel.send(error_msg)
            else:
                await message.channel.send(error_msg)
    
    @commands.command(name='help', aliases=['h', 'مساعدة', 'اوامر'])
    async def help_command(self, ctx):
        embed = discord.Embed(
            title="🤖 **بوت الترجمة المتطور**",
            description="""
            **أرسل أي صورة وسأقوم بـ:**
            ✅ استخراج النص منها
            ✅ ترجمته إلى العربية
            ✅ عرض النص الأصلي والمترجم
            """,
            color=0x00ff00
        )
        
        embed.add_field(
            name="🌐 **اللغات المدعومة**",
            value="• كوري\n• عربي\n• إنجليزي\n• ياباني\n• صيني",
            inline=True
        )
        
        embed.add_field(
            name="⚡ **المميزات**",
            value="• صور حتى 50 ميجا\n• أبعاد حتى 15000 بكسل\n• تقسيم تلقائي\n• ترجمة فورية",
            inline=True
        )
        
        embed.add_field(
            name="📊 **الأوامر**",
            value="`!stats` - الإحصائيات\n`!help` - هذه المساعدة\n`!ping` - اختبار الاتصال",
            inline=False
        )
        
        embed.set_footer(text=f"شغال منذ {self.get_uptime()}")
        await ctx.send(embed=embed)
    
    @commands.command(name='stats', aliases=['احصائيات', 'stat'])
    async def stats_command(self, ctx):
        delta = datetime.now() - self.start_time
        hours = int(delta.total_seconds() // 3600)
        minutes = int((delta.total_seconds() % 3600) // 60)
        seconds = int(delta.total_seconds() % 60)
        
        embed = discord.Embed(
            title="📊 **إحصائيات البوت**",
            color=0x3498db,
            timestamp=datetime.now()
        )
        
        embed.add_field(name="⏱️ **وقت التشغيل**", value=f"{hours} س {minutes} د {seconds} ث", inline=True)
        embed.add_field(name="📸 **صور مترجمة**", value=str(self.count), inline=True)
        embed.add_field(name="⚙️ **الحالة**", value="✅ شغال", inline=True)
        embed.add_field(name="🌐 **الـ OCR**", value="OCR.Space", inline=True)
        embed.add_field(name="🌍 **الترجمة**", value="Google Translate", inline=True)
        embed.add_field(name="📦 **الإصدار**", value="v2.0 (نهائي)", inline=True)
        
        embed.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='ping', aliases=['بنج'])
    async def ping_command(self, ctx):
        """اختبار سرعة الاتصال"""
        latency = round(self.latency * 1000)
        embed = discord.Embed(
            title="🏓 **Pong!**",
            description=f"⏱️ زمن الاستجابة: **{latency}ms**",
            color=0x00ff00 if latency < 200 else 0xffaa00 if latency < 400 else 0xff0000
        )
        await ctx.send(embed=embed)
    
    @commands.command(name='clear_temp', aliases=['مسح'])
    @commands.has_permissions(administrator=True)
    async def clear_temp_command(self, ctx):
        """مسح الرسائل المؤقتة (للمشرفين فقط)"""
        count = 0
        for msg in self.temp_messages:
            try:
                await msg.delete()
                count += 1
            except:
                pass
        self.temp_messages.clear()
        await ctx.send(f"✅ تم مسح {count} رسالة مؤقتة")
    
    def get_uptime(self):
        """حساب وقت التشغيل"""
        delta = datetime.now() - self.start_time
        hours = int(delta.total_seconds() // 3600)
        minutes = int((delta.total_seconds() % 3600) // 60)
        
        if hours > 0:
            return f"{hours} ساعة و {minutes} دقيقة"
        else:
            return f"{minutes} دقيقة"
    
    async def close(self):
        """إغلاق البوت بشكل نظيف"""
        logger.info("🔄 جاري إغلاق البوت...")
        
        # مسح الرسائل المؤقتة
        for msg in self.temp_messages:
            try:
                await msg.delete()
            except:
                pass
        
        await super().close()
        logger.info("✅ تم إغلاق البوت")
