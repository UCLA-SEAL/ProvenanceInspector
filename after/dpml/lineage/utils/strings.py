import unicodedata
import re

ACCENT_LATIN_PATTERN = r'[ÆÐØÞßæðøþŒœƒ]'

def strip_accents(text):
    return ''.join(c for c in unicodedata.normalize('NFKD', text) if unicodedata.category(c) != 'Mn')

def strip_accent_letter(text):
    return re.sub(ACCENT_LATIN_PATTERN, '', text)

def words_from_text(s, words_to_ignore=[]):
    homos = set(
        [
            "˗",
            "৭",
            "Ȣ",
            "𝟕",
            "б",
            "Ƽ",
            "Ꮞ",
            "Ʒ",
            "ᒿ",
            "l",
            "O",
            "`",
            "ɑ",
            "Ь",
            "ϲ",
            "ԁ",
            "е",
            "𝚏",
            "ɡ",
            "հ",
            "і",
            "ϳ",
            "𝒌",
            "ⅼ",
            "ｍ",
            "ո",
            "о",
            "р",
            "ԛ",
            "ⲅ",
            "ѕ",
            "𝚝",
            "ս",
            "ѵ",
            "ԝ",
            "×",
            "у",
            "ᴢ",
        ]
    )
    """Lowercases a string, removes all non-alphanumeric characters, and splits
    into words."""
    # TODO implement w regex
    words = []
    word = ""
    s = " ".join(s.split())

    for c in s:
        if c.isalnum() or c in homos:
            word += c
        elif c in "'-_*@" and len(word) > 0:
            # Allow apostrophes, hyphens, underscores, asterisks and at signs as long as they don't begin the
            # word.
            word += c
        elif word:
            if word not in words_to_ignore:
                words.append(word)
            word = ""
    if len(word) and (word not in words_to_ignore):
        words.append(word)
    return words

