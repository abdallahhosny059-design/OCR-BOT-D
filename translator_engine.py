import openai
import logging
from config import OPENAI_API_KEY

logger = logging.getLogger(__name__)

class TranslatorEngine:
    def __init__(self):
        openai.api_key = OPENAI_API_KEY
        
    def translate(self, text):
        try:
            if not text or len(text) < 3:
                return None
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "أنت مترجم محترف لقصص المانهوا. ترجم النص التالي إلى العربية الفصحى بأسلوب أدبي."},
                    {"role": "user", "content": f"ترجم: {text}"}
                ]
            )
            
            translated = response.choices[0].message.content
            return translated.strip('"').strip("'").strip()
            
        except Exception as e:
            logger.error(f"Translation Error: {e}")
            return None
