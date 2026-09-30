import json 
import threading 

from pathlib import Path 
from translator import config 

APP_DIR = Path.home() / "Library" / "Application Support" / "Translator"
SETTING_PATH = APP_DIR / "setting.json"

DEFAULTS = {
    "gemini_api_key": "",
    "groq_api_key": "",
    "custom_prompt": "",
    "auto_dictionary": True,
    "font_size": 16.0,
}

class SettingsStore:
    def __init__(self, path: Path = SETTING_PATH):
        self._path = path 
        self._lock = threading.RLock()
        self._data = dict(DEFAULTS)
        self._load()
    def _load(self):
        try: 
            with open(self._path, "r", encoding="utf-8") as f:
                stored = json.load(f)
            if isinstance(stored, dict):
                self._data.update({k: stored[k] for k in DEFAULTS if k in stored})
        except (OSError, json.JSONDecodeError):
            pass 

    def _save(self):
        self._path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self._path.with_suffix(".json.tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)
        tmp.replace(self._path)

    def get(self, key):
        with self._lock:
            return self._data.get(key, DEFAULTS.get(key))

    def set(self, key, value):
        with self._lock:
            if self._data.get(key) == value:
                return 
            self._data[key] = value 
            self._save()
    def effective_prompt(self) -> str:
        return (self.get("custom_prompt") or "").strip() or config.DEFAULT_PROMPT
