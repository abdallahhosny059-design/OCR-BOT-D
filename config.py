import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
OCR_API_KEY = os.getenv('OCR_API_KEY')  # من OCR.Space
SUPPORTED_FORMATS = ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp']
