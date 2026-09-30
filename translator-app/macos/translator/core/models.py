from dataclasses import dataclass, field 
from typing import Optional 

@dataclass 
class TranslationResult:
    original: str 
    translated: str 
    provider: str 

@dataclass 
class Definition:
    text: str 
    example: Optional[str] = None 

@dataclass 
class Meaning:
    part_of_speech: str 
    definitions: list = field(default_factory=list)
    synonyms: list = field(default_factory=list)
    antonyms: list = field(default_factory=list)

@dataclass 
class DictionaryEntry:
    word: str 
    phonetic: str = ""
    audio_url: str = ""
    meanings: list = field(default_factory=list)
