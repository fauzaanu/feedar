# Helpers that are related to formatting and text manipulation

from string import ascii_letters, punctuation

from dhivehi_nlp import stemmer


def is_dhivehi_word(word: str):
    """
    Is it a dhivehi word?
    """
    for letter in word:
        if letter in ascii_letters:
            return False

        if letter is ' ':
            continue

        # \u0780-\u07B1 is the range of dhivehi letters in the thaana unicode block -
        # (https://github.com/hadithmv/hadithmv.github.io/blob/ebc8c9780b9e5d9f9551ea69f06c4a2862301541/js/quranHmv-script.js#L1113)
        if letter not in [chr(i) for i in range(1920, 1970)]:  # 1920 to 1970 is the range of thaana unicode block
            return False
    return True


def remove_punctuation(word: str):
    """
    Remove punctuation from word
    """
    return ''.join([char for char in word if char not in punctuation])


def remove_all_english(text: str):
    """
    Remove all english words from text
    """
    for word in text.split():
        for letter in word:
            if letter in ascii_letters:
                text = text.replace(word, '')
            if letter in punctuation:
                text = text.replace(word, '')
            if letter not in [chr(i) for i in range(1920, 1970)]:
                text = text.replace(word, '')
    return text


def preprocess_word(word):
    word = word.lower()
    word = remove_punctuation(word)
    stemmed_word = stemmer.stem(word)

    if type(stemmed_word) == list:
        if stemmed_word:
            word = stemmed_word[0]

    return word


