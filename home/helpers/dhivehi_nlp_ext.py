# extension functions for dhivehi nlp library - accessing the sqlite database they have
import json

from dhivehi_nlp import dictionary
from dhivehi_nlp._helpers import _db_connect

from home.helpers.formatting import remove_punctuation
from home.models import Word, Meaning


def get_related_words(filter: str):
    """
    Searches the definitions for the filter and returns a list of related words.
    """
    con = _db_connect()
    cursor = con.cursor()

    query = f"SELECT word FROM radheef WHERE definition LIKE '%{filter}%'"
    cursor.execute(query)
    words = [word[0] for word in cursor.fetchall()]
    return words


def process_related_words(word):
    """
    Process related words for a given word
    """
    related_words = get_related_words(filter=word)
    with open('related_words.txt', 'w', encoding='utf-8') as f:
        f.write(json.dumps(related_words))
    if related_words:
        q_word, _ = Word.objects.get_or_create(word=word)
        for related_word in related_words:
            r_word, _ = Word.objects.get_or_create(word=related_word)
            q_word.related_words.add(r_word)
            q_word.save()

    return True


def process_meaning(word, meaning):
    """
    Most likely this will never run as we initially move everything in sqlite to our database
    """
    word_obj, _ = Word.objects.get_or_create(word=word)

    for mean in meaning:
        mean = remove_punctuation(mean)
        if mean:
            Meaning.objects.get_or_create(meaning=mean, word=word_obj)

    word_length = len(word)
    for i in range(word_length):
        wrd = word[:word_length - i]
        meaning = dictionary.get_definition(wrd)
        if meaning:
            related_word, _ = Word.objects.get_or_create(word=wrd)
            word_obj.related_words.add(related_word)
            word_obj.save()

            for meaning_item in meaning:
                meaning_item = remove_punctuation(meaning_item)
                if meaning_item:
                    Meaning.objects.get_or_create(meaning=meaning_item, word=related_word)

    return True
