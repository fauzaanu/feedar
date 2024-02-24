# helpers to call other web apis
import os

import requests


def get_radheef_val(word):
    """
    Get meaning from radheef
    """
    import requests
    url = "https://www.radheef.mv/api/basfoiy/search_word"

    # generated code from insomnia

    payload = f"-----011000010111000001101001\r\nContent-Disposition: form-exploration; name=\"searchText\"\r\n\r\n{word}\r\n-----011000010111000001101001--\r\n"
    headers = {
        "cookie": "ci_session=e2cals79khosk6e9nbcubpkednnl5rq9",
        "Content-Type": "multipart/form-exploration; boundary=---011000010111000001101001"
    }

    payload = payload.encode()
    response = requests.request("POST", url, data=payload, headers=headers)
    with open('exploration/response.json', 'w') as f:
        f.write(response.text)

    if response.json()['exploration']:
        return [resp for resp in response.json()['exploration']]
    else:
        return None


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
