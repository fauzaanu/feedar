import json


def query_dhivehi_mv_api(word: str):
    """
    Query dhivehi.mv api for word,
    multipart-form exploration
    type=lt&text=word
    """
    import requests

    url = "https://dhivehi.mv/api/latin-thaana/"

    payload = ("-----011000010111000001101001\r\nContent-Disposition: form-exploration; "
               "name=\"type\"\r\n\r\nlt\r\n-----011000010111000001101001\r\nContent-Disposition: form-exploration; "
               f"name=\"text\"\r\n\r\n{word}\r\n-----011000010111000001101001--\r\n\r\n")
    headers = {"content-type": "multipart/form-exploration; boundary=---011000010111000001101001"}

    response = requests.post(url, data=payload, headers=headers)
    return response


def get_pronounciation(word: str):
    """
    get pronounciation from common voice
    Downloads a mp3 file. but where do we store this lol.
    Locally...
    So a file server can be possible..
    """
    import requests
    url = f"https://dhivehi.mv/tools/tts/data/?g=female&q={word}"
    response = requests.get(url)
    return response


if __name__ == "__main__":
    x = query_dhivehi_mv_api('ދަނޑިވަޅު')
    with open('response.txt', 'w', encoding='utf-8') as f:
        f.write(x.text)

# hmm we dont really need to query too. let the client side handle this
