from typing import Optional

from translator import config
from translator.core.translation.base import TranslationProvider
from translator.utils import http


class GroqProvider(TranslationProvider):
    name = "Groq"

    def is_configured(self) -> bool:
        return bool(self._settings.get("groq_api_key").strip())

    def _translate(self, text: str) -> Optional[str]:
        headers = {"Authorization": f"Bearer {self._settings.get('groq_api_key').strip()}"}
        for model in config.GROQ_MODELS:
            try:
                response = http.session.post(
                    config.GROQ_URL,
                    headers=headers,
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": self._settings.effective_prompt()},
                            {"role": "user", "content": text},
                        ],
                        "temperature": 0.3,
                    },
                    timeout=config.REQUEST_TIMEOUT,
                )
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"].strip()
            except Exception as exc:
                print(f"[Groq/{model}] {exc}")
        return None
