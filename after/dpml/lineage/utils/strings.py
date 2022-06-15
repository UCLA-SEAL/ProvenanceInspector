from ..le_token import LeToken

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


def tokens_from_text(s, words_to_ignore=[]):
    """
    split text into list of tokens <LeToken>, where their are both words and non-words tokens.
    """
    words = words_from_text(s, words_to_ignore=words_to_ignore)
    tokens = []

    cur_text = s
    for word in words:
        word_start = cur_text.index(word)
        word_end = word_start + len(word)

        if cur_text[:word_start]:
            tokens.append(LeToken(cur_text[:word_start], le_attrs={'is_word': False})) # non-word token
        
        tokens.append(LeToken(word, le_attrs={'is_word': True})) # word token
        
        cur_text = cur_text[word_end:] # unprocessed text

    if cur_text:
        tokens.append(LeToken(cur_text, le_attrs={'is_word': False}))

    return tokens
