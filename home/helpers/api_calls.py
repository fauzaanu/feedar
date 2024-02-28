# helpers to call other web apis
import os
from pprint import pprint

import requests


def get_radheef_val(word):
    """
    Get meaning from radheef
    """
    import requests

    url = "https://www.radheef.mv/api/basfoiy/search_word"

    payload = f"-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"searchText\"\r\n\r\n{word}\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"\"\r\n\r\n\r\n-----011000010111000001101001--\r\n\r\n"
    headers = {"content-type": "multipart/form-data; boundary=---011000010111000001101001"}

    response = requests.post(url, data=payload, headers=headers)

    if response.status_code != 200:
        return False

    meanings = response.json()['data']
    meanings_list = []
    for meaning in meanings:
        if meaning.get('meaning_text'):
            meanings_list.append(meaning['meaning_text'])

    return meanings_list




def google_custom_search_api(word):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': os.getenv('GOOGLE_SEARCH_API_KEY'),
        'cx': os.getenv('CX'),
        'q': word,
        'exactTerms': word
    }
    response = requests.get(url, params=params)
    return response
