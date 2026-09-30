import re 

_WORD_RE = re.compile(r"^[A-Za-z][A-Za-z'’-]*$")
_PUNCT = ".,!?;:\"'“”«»()[]{}…"


def normalize_word(text: str) -> str:
    return text.strip().strip(_PUNCT)


def is_single_english_word(text: str) -> bool:
    word = normalize_word(text)
    return bool(_WORD_RE.match(word)) and len(word) <= 40