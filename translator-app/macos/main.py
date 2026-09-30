from translator.app import TranslatorApp
from translator.core.dictionary import FreeDictionaryClient
from translator.core.translation import (
    GeminiProvider, GoogleFreeProvider, GroqProvider, TranslationService,
)
from translator.settings.store import SettingsStore


def main():
    settings = SettingsStore()
    service = TranslationService([
        GeminiProvider(settings),
        GroqProvider(settings),
        GoogleFreeProvider(settings),  #always last (weaker translator than LLMs in sentence)
    ])
    app = TranslatorApp(settings, service, FreeDictionaryClient())
    app.run()


if __name__ == "__main__":
    main()