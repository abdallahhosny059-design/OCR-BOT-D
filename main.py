import logging
from bot import ManhwaBot
from config import DISCORD_TOKEN

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("❌ توكن الديسكورد مفقود!")
    else:
        bot = ManhwaBot()
        bot.run(token=DISCORD_TOKEN)  # 👈 تم التعديل هنا
