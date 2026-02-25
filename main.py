import logging
from bot import LegendaryManhwaBot
from config import DISCORD_TOKEN

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("❌ توكن الديسكورد مفقود!")
    else:
        bot = LegendaryManhwaBot()
        bot.run(DISCORD_TOKEN)
