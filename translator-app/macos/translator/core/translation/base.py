from abc import ABC, abstractmethod
from typing import Optional

from translator.settings.store import SettingsStore

class TranslationProvider(ABC):
    name: str = "provider"

    def __init__(self, settings: SettingsStore):
        self._settings = settings 

    @abstractmethod
    def is_configured(self) -> bool:
        ...

    @abstractmethod
    def _translate(self, text: str) -> Optional[str]:
        ...

    def translate(self, text: str) -> Optional[str]:
        if not self.is_configured():
            return None 
        try:
            return self._translate(text)
        except Exception as exc:
            print(f"[{self.name}]: {exc}")
            return None 


