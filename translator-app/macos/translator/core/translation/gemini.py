from typing import Optional 

from translator import config 
from translator.core.translation.base import TranslationProvider
from translator.utils import http 

class GeminiProvider(TranslationProvider):
    name = "Gemini"

    def is_configured(self) -> bool:
        return bool(self._settings.get("gemini_api_key").strip())

    def _translate(self, text: str) -> Optional[str]:
        key = self._settings.get("gemini_api_key").strip()
        url = config.GEMINI_URL.format(model=config.GEMINI_MODEL, key=key)
        response = http.session.post(
            url, 
            json={
                "system_instruction": {"parts": [{"text": self._settings.effective_prompt()}]},
                "contents": [{"parts": [{"text": text}]}],
                "generationConfig": {"temperature": 0.3},
            },
            timeout=config.REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()