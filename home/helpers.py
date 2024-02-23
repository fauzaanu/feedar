import json
import os
from datetime import date
from string import ascii_letters, punctuation

import requests
from dhivehi_nlp._helpers import _db_connect

from home.models import SearchResponse, Word


def is_dhivehi_word(word: str):
    """
    Is it a dhivehi word?
    """
    for letter in word:
        if letter in ascii_letters:
            return False

        # \u0780-\u07B1 is the range of dhivehi letters in the thaana unicode block -
        # (https://github.com/hadithmv/hadithmv.github.io/blob/ebc8c9780b9e5d9f9551ea69f06c4a2862301541/js/quranHmv-script.js#L1113)
        if letter not in [chr(i) for i in range(1920, 1985)]:  # 1920 to 1970 is the range of thaana unicode block
            return False
    return True


def remove_punctuation(word: str):
    """
    Remove punctuation from word
    """
    return ''.join([char for char in word if char not in punctuation])


def get_radheef_val(word):
    """
    Get meaning from radheef
    """
    import requests
    url = "https://www.radheef.mv/api/basfoiy/search_word"

    # generated code from insomnia

    payload = f"-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"searchText\"\r\n\r\n{word}\r\n-----011000010111000001101001--\r\n"
    headers = {
        "cookie": "ci_session=e2cals79khosk6e9nbcubpkednnl5rq9",
        "Content-Type": "multipart/form-data; boundary=---011000010111000001101001"
    }

    payload = payload.encode()
    response = requests.request("POST", url, data=payload, headers=headers)
    with open('response.json', 'w') as f:
        f.write(response.text)

    if response.json()['data']:
        return [resp for resp in response.json()['data']]
    else:
        return None


def google_custom_search(word):
    word_obj, _ = Word.objects.get_or_create(word=word)

    if SearchResponse.objects.filter(word=word_obj).exists():
        return SearchResponse.objects.get(word=word_obj)

    # check if our daily limit is above 100
    current_requests = SearchResponse.objects.filter(date=date.today()).count()
    print(current_requests)
    if current_requests > 100:
        return None

    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': os.getenv('GOOGLE_SEARCH_API_KEY'),
        'cx': os.getenv('CX'),
        'q': word,
        'exactTerms': word
    }
    response = requests.get(url, params=params)
    response_json = json.dumps(response.json())
    search_results = SearchResponse.objects.create(word=word_obj, response=response_json)
    return search_results


def get_related_words(filter=None):
    """
    Searches the definitions for the filter and returns a list of related words.
    """
    con = _db_connect()
    cursor = con.cursor()

    if filter:
        query = f"SELECT word FROM radheef WHERE definition LIKE '%{filter}%'"
    else:
        query = "SELECT word FROM radheef"
    cursor.execute(query)
    words = [word[0] for word in cursor.fetchall()]
    return words