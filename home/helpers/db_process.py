from typing import Union, Literal

from home.helpers.formatting import remove_punctuation
from home.models import Meaning, Word

# Define custom types for the allowed string values
DhivehiNLP = Literal['DhivehiNLP']
RadheefMV = Literal['radheef.mv']


def process_meaning(meanings: list, word: Word, source: Union[DhivehiNLP, RadheefMV]):
    for meaning in meanings:
        meaning = remove_punctuation(meaning)
        meaning, _ = Meaning.objects.get_or_create(meaning=meaning, word=word, source=source)
