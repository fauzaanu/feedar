# extension functions for dhivehi nlp library - accessing the sqlite database they have
import json

from dhivehi_nlp._helpers import _db_connect

from home.helpers.mynameisroot import hey_root
from home.models import Word


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


# def process_meaning(word, meaning):
#     """
#     Most likely this will never run as we initially move everything in sqlite to our database
#     """
#     word_obj, _ = Word.objects.get_or_create(word=word)
#
#     for mean in meaning:
#         mean = remove_punctuation(mean)
#         if mean:
#             Meaning.objects.get_or_create(meaning=mean, word=word_obj)
#
#     word_length = len(word)
#     for i in range(word_length):
#         wrd = word[:word_length - i]
#         meaning = dictionary.get_definition(wrd)
#         if meaning:
#             related_word, _ = Word.objects.get_or_create(word=wrd)
#             word_obj.related_words.add(related_word)
#             word_obj.save()
#
#             for meaning_item in meaning:
#                 meaning_item = remove_punctuation(meaning_item)
#                 if meaning_item:
#                     Meaning.objects.get_or_create(meaning=meaning_item, word=related_word)
#
#     return True



def get_part_of_speech(word):
    """
    Get the part of speech from dhivehi nlp db
    """
    con = _db_connect()
    cursor = con.cursor()
    query = f"SELECT part_of_speech FROM radheef WHERE word='{word}'"
    cursor.execute(query)
    result = cursor.fetchone()
    con.close()
    if result is None:
        return None

    part_of_speech_convert = {
        'ނަން': 'nan',
        'ކަން': 'kan',
        'ނަންއިތުރު': 'nan ithuru',
        'ކަންއިތުރު': 'kan ithuru',
        'މަސްދަރު': 'masdharu',
        'ނަންއިތުރުގެ ނަން': 'nan ithuruge nan',
        'އިތުރު': 'ithuru',
        'އަކުރު': 'akuru'
    }

    if result[0] in part_of_speech_convert:
        return part_of_speech_convert[result[0]]
    elif result[0] == None:
        return None
    else:
        message = f"""
# Un-recognized part of speech

> While processing the part of speech for the word {word}, we encountered an un-recognized part of speech.

word: {word}
part of speech: {result[0]}       
"""
        hey_root(message)
        raise ValueError(f"Un-regconized part of speech: {result[0]}")