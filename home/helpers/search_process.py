from datetime import date

from home.helpers.api_calls import google_custom_search_api
from home.helpers.formatting import remove_all_english
from home.models import Word, Webpage, SearchResponse





def find_sentence_with_word(text, word):
    # split into chucks of 500 words
    chunks = [text[i:i + 250] for i in range(0, len(text), 250)]
    sentences = [chunk for chunk in chunks if word in chunk]

    for sentence in sentences:
        return sentence

    return None
