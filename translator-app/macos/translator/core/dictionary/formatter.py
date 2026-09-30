from translator.core.models import DictionaryEntry 

MAX_SENSES_PER_POS = 3 
MAX_SYNONYMS = 6 

def format_entry(entry: DictionaryEntry) -> str:
    header = entry.word 
    if entry.phonetic:
        header += f"   {entry.phonetic}"
    lines = [header]
    for meaning in entry.meanings:
        lines += ["", meaning.part_of_speech.lower()]
        for i, definition in enumerate(meaning.definitions[:MAX_SENSES_PER_POS], 1):
            lines.append(f"{i}. {definition.text}")
            if definition.example:
                lines.append(f'     "{definition.example}"')
        if meaning.synonyms:
            lines.append(f"synonyms: {', '.join(meaning.synonyms[:MAX_SYNONYMS])}")
    return "\n".join(lines)