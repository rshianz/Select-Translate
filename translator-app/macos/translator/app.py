import queue
import threading

import rumps

from translator.core.dictionary import FreeDictionaryClient, format_entry
from translator.core.translation import TranslationService
from translator.hotkeys.listener import KEY_D, KEY_SPACE, HotkeyHub
from translator.settings.store import SettingsStore
from translator.ui import floating_window
from translator.ui.font_slider import build_font_size_menu_item
from translator.ui.main_window import MainWindowController
from translator.ui.settings_window import SettingsWindowController
from translator.utils.clipboard import get_selected_text
from translator.utils.text import is_single_english_word, normalize_word


class TranslatorApp(rumps.App):
    def __init__(self, settings, translation_service, dictionary_client):
        super().__init__("🌐", title="🌐 Translate")
        self.settings = settings
        self._translation = translation_service
        self._dictionary = dictionary_client

        self._hotkeys = HotkeyHub()
        self._translate_flag = self._hotkeys.register(KEY_SPACE)
        self._define_flag = self._hotkeys.register(KEY_D)

        self._main_queue = queue.Queue()
        self._main_window = None
        self._settings_window = None

        self.menu = [
            rumps.MenuItem("Open Translator", self.show_main_window),
            rumps.MenuItem("Settings…", self.show_settings),
            None,
            rumps.MenuItem("Translate Selected Text  (⌃Space)", self.request_translate),
            rumps.MenuItem("Define Selected Word  (⌃D)", self.request_define),
            None,
            build_font_size_menu_item(self.settings.get("font_size"), self._on_font_change),
        ]

        self._timer = rumps.Timer(self._tick, 0.05)
        self._timer.start()

        self._launch_timer = rumps.Timer(self._on_launch, 0.3)
        self._launch_timer.start()

        self._hotkeys.start()

    # ---------------------------------------------- main-thread plumbing
    def run_on_main(self, fn):
        self._main_queue.put(fn)

    def _tick(self, _):
        if self._translate_flag.is_set():
            self._translate_flag.clear()
            self.request_translate()
        if self._define_flag.is_set():
            self._define_flag.clear()
            self.request_define()
        while True:
            try:
                job = self._main_queue.get_nowait()
            except queue.Empty:
                break
            try:
                job()
            except Exception as exc:
                print(f"[UI] {exc}")

    def _on_launch(self, _):
        self._launch_timer.stop()
        self.show_main_window()

    # -------------------------------------------------------- windows
    def show_main_window(self, _=None):
        if self._main_window is None:
            self._main_window = MainWindowController.alloc().initWithApp_(self)
        self._main_window.show()

    def show_settings(self, _=None):
        if self._settings_window is None:
            self._settings_window = SettingsWindowController.alloc().initWithApp_settings_(
                self, self.settings)
        self._settings_window.show()

    def on_settings_changed(self):
        if self._main_window is not None:
            self._main_window.refresh_status()

    def provider_status(self):
        return [(p.name, p.is_configured()) for p in self._translation.providers]

    def _show(self, message, title, rtl=True):
        size = self.settings.get("font_size")
        self.run_on_main(
            lambda: floating_window.show(message, title, rtl=rtl, font_size=size))

    # ------------------------------- async helpers (main-window buttons)
    def translate_async(self, text, on_result):
        def work():
            result = self._translation.translate(text)
            self.run_on_main(lambda: on_result(result))
        threading.Thread(target=work, daemon=True).start()

    def define_async(self, word, on_entry):
        def work():
            entry = self._dictionary.lookup(word)
            self.run_on_main(lambda: on_entry(entry))
        threading.Thread(target=work, daemon=True).start()

    # ---------------------------------- hotkey entry points (main thread)
    def request_translate(self, _=None):
        text = get_selected_text()
        if not text.strip():
            self._show("No text selected", "Error")
            return
        threading.Thread(target=self._translate_worker, args=(text,),
                         daemon=True).start()

    def request_define(self, _=None):
        text = get_selected_text()
        tokens = [normalize_word(t) for t in text.split()]
        word = next((t for t in tokens if t), "")
        if not word:
            self._show("No text selected", "Error")
            return
        threading.Thread(target=self._define_worker, args=(word,),
                         daemon=True).start()

    # --------------------------------- workers (background threads, network only)
    def _translate_worker(self, text):
        if self.settings.get("auto_dictionary") and is_single_english_word(text):
            threading.Thread(
                target=self._dictionary_flow,
                args=(normalize_word(text),),
                daemon=True,
            ).start()

        result = self._translation.translate(text)
        if result:
            self._show(result.translated, result.provider, rtl=True)
        else:
            self._show("Translation failed", "Error")

    def _dictionary_flow(self, word):
        entry = self._dictionary.lookup(word)
        if entry:
            self._show(format_entry(entry), "Dictionary", rtl=False)

    def _define_worker(self, word):
        entry = self._dictionary.lookup(word)
        if entry:
            self._show(format_entry(entry), "Dictionary", rtl=False)
        else:
            self._show(f"No definition found for “{word}”", "Dictionary", rtl=False)

    # -------------------------------------------------------- settings
    def _on_font_change(self, size):
        self.settings.set("font_size", size)
        floating_window.set_font_size_for_all(size)