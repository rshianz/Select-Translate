"""Static defaults & endpoints.

Everything user-editable (API keys, prompt, font size…) lives in
translator/settings/store.py — NOT here.
"""

DEFAULT_PROMPT = (
    "You are a translation assistant. Translate the user's text to "
    "Persian (Farsi). Only return the translation, nothing else."
)

TARGET_LANGUAGE = "fa"

GEMINI_MODEL = "gemini-3.5-flash-lite"
GROQ_MODELS = ["openai/gpt-oss-120b", "openai/gpt-oss-20b"]

GEMINI_URL = ("https://generativelanguage.googleapis.com/v1beta/"
              "models/{model}:generateContent?key={key}")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# --- dictionary ---------------------------------------------------------
DICTIONARY_API_BASE = "https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
WIKTIONARY_API_BASE = "https://en.wiktionary.org/api/rest_v1/page/definition/{word}"
DICTIONARY_TIMEOUT = 20      # seconds per HTTP request — the API is SLOW
DICTIONARY_HEDGE_DELAY = 4   # seconds before the Wiktionary fallback fires

REQUEST_TIMEOUT = 15