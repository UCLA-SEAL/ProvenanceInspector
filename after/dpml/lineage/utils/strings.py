from textattack.shared.utils import words_from_text

from ..le_token import LeToken


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
