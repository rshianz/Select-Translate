from deep_translator import GoogleTranslator

from translator import config 
from translator.core.translation.base import TranslationProvider

class GoogleFreeProvider(TranslationProvider):
    name="Google Translate"

    def is_configured(self) -> bool:
        return True 

    def _translate(self, text: str) -> str:
        return GoogleTranslator(source="auto", target=config.TARGET_LANGUAGE).translate(text)
        