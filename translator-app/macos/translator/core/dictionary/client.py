import re
import threading
import urllib.parse
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor, as_completed, wait
from typing import Optional

from translator import config
from translator.core.models import Definition, DictionaryEntry, Meaning
from translator.utils import http

CACHE_LIMIT = 512
_TAG_RE = re.compile(r"<[^>]+>")


def _strip_tags(text: str) -> str:
    return _TAG_RE.sub("", text).strip()


class FreeDictionaryClient:
    def __init__(self):
        self._cache = OrderedDict()
        self._lock = threading.Lock()
        self._pool = ThreadPoolExecutor(max_workers=6, thread_name_prefix="dict")

    def lookup(self, word: str) -> Optional[DictionaryEntry]:
        word = word.strip().lower()
        if not word:
            return None

        with self._lock:
            if word in self._cache:
                self._cache.move_to_end(word)
                return self._cache[word]

        futures = {
            self._pool.submit(self._fetch_dev, http.dictionary_session, word, "proxy"),
            self._pool.submit(self._fetch_dev, http.direct_session, word, "direct"),
        }
        done, pending = wait(futures, timeout=config.DICTIONARY_HEDGE_DELAY)
        entry = self._first_success(done)

        if entry is None:
            pending.add(self._pool.submit(
                self._fetch_wiktionary, http.dictionary_session, word, "proxy"))
            pending.add(self._pool.submit(
                self._fetch_wiktionary, http.direct_session, word, "direct"))
            for future in as_completed(pending):
                try:
                    result = future.result()
                except Exception:
                    continue
                if result is not None:
                    entry = result
                    break

        if entry is not None:
            with self._lock:
                self._cache[word] = entry
                while len(self._cache) > CACHE_LIMIT:
                    self._cache.popitem(last=False)
        return entry

    @staticmethod
    def _first_success(futures) -> Optional[DictionaryEntry]:
        for future in futures:
            try:
                result = future.result()
            except Exception:
                continue
            if result is not None:
                return result
        return None

    def _fetch_dev(self, session, word: str, route: str) -> Optional[DictionaryEntry]:
        try:
            response = session.get(
                config.DICTIONARY_API_BASE.format(word=word),
                timeout=config.DICTIONARY_TIMEOUT,
            )
            if response.status_code == 404:
                return None
            response.raise_for_status()
            data = response.json()
        except Exception as exc:
            print(f"[Dictionary/dev/{route}] {exc}")
            return None
        if not isinstance(data, list) or not data:
            return None
        return self._parse_dev(data[0])

    def _fetch_wiktionary(self, session, word: str, route: str) -> Optional[DictionaryEntry]:
        try:
            response = session.get(
                config.WIKTIONARY_API_BASE.format(word=urllib.parse.quote(word)),
                timeout=config.DICTIONARY_TIMEOUT,
            )
            if response.status_code == 404:
                return None
            response.raise_for_status()
            data = response.json()
        except Exception as exc:
            print(f"[Dictionary/wiktionary/{route}] {exc}")
            return None
        return self._parse_wiktionary(word, data)

    @staticmethod
    def _parse_dev(data: dict) -> DictionaryEntry:
        phonetic = data.get("phonetic") or next(
            (p["text"] for p in data.get("phonetics", []) if p.get("text")), "")
        audio_url = next(
            (p["audio"] for p in data.get("phonetics", []) if p.get("audio")), "")
        meanings = [
            Meaning(
                part_of_speech=m.get("partOfSpeech", ""),
                definitions=[
                    Definition(text=d.get("definition", ""), example=d.get("example"))
                    for d in m.get("definitions", [])
                ],
                synonyms=m.get("synonyms", []),
                antonyms=m.get("antonyms", []),
            )
            for m in data.get("meanings", [])
        ]
        return DictionaryEntry(data.get("word", ""), phonetic, audio_url, meanings)

    @staticmethod
    def _parse_wiktionary(word: str, data: dict) -> Optional[DictionaryEntry]:
        sections = data.get("en") or []
        meanings = []
        for section in sections:
            definitions = []
            for d in section.get("definitions", []):
                text = _strip_tags(d.get("definition", ""))
                if not text:
                    continue
                examples = d.get("examples") or []
                example = _strip_tags(examples[0]) if examples else None
                definitions.append(Definition(text=text, example=example))
            if definitions:
                meanings.append(Meaning(
                    part_of_speech=section.get("partOfSpeech", ""),
                    definitions=definitions,
                ))
        if not meanings:
            return None
        return DictionaryEntry(word, "", "", meanings)