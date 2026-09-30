from typing import Optional, Sequence

from translator.core.models import TranslationResult
from translator.core.translation.base import TranslationProvider

class TranslationService:
    def __init__(self, providers: Sequence[TranslationProvider]):
        self.providers = list(providers)

    def translate(self, text: str) -> Optional[TranslationResult]:
        for provider in self.providers:
            translated = provider.translate(text)
            if translated:
                return TranslationResult(text, translated, provider.name)
        return None 
        