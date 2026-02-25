import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
SUPPORTED_FORMATS = ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'tiff']
