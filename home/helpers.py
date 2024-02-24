import json
import os
from datetime import date
from string import ascii_letters, punctuation
from bs4 import BeautifulSoup
import requests
from dhivehi_nlp import dictionary, stemmer
from dhivehi_nlp._helpers import _db_connect

from home.models import SearchResponse, Word, Meaning, Webpage


def is_dhivehi_word(word: str):
    """
    Is it a dhivehi word?
    """
    for letter in word:
        if letter in ascii_letters:
            return False

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


def google_custom_search(word):
    word_obj, _ = Word.objects.get_or_create(word=word)

    # do we have Webpage objects for this word?
    if Webpage.objects.filter(words__word=word).exists():
        all_pages = Webpage.objects.filter(words__word=word)
        for page in all_pages:
            if page.text_section:
                # remove english words
                text = page.text_section
                for word in text.split():
                    for letter in word:
                        if letter in ascii_letters:
                            text = text.replace(word, '')
                        if letter in punctuation:
                            text = text.replace(word, '')
                        if letter not in [chr(i) for i in range(1920, 1970)]:
                            text = text.replace(word, '')

                if text.isspace():
                    page.delete()
                page.text_section = text
                page.save()
        return None

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

    # get all the links from the response
    items = response.json()['items']
    for item in items:
        url = item['link']
        page, _ = Webpage.objects.get_or_create(url=url)
        page.words.add(word_obj)

        page.text_content = extract_text_from_html(url)

        sentence = find_sentence_with_word(page.text_content, word)
        if sentence:
            if not str(sentence).isspace():
                page.text_section = sentence
                page.save()

    return True


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

    # get the search result
    google_custom_search(word)
    return True


def preprocess_word(word):
    word = word.lower()
    word = remove_punctuation(word)
    word = stemmer.stem(word)

    if type(word) == list:
        word = word[0]

    return word


def extract_text_from_html(url):
    response = requests.get(url)
    html_content = response.content

    soup = BeautifulSoup(html_content, 'html.parser')

    # Remove script tags
    for script in soup(['script', 'style']):
        script.extract()

    # Get all text
    text = soup.get_text()

    # remove english words
    for word in text.split():
        for letter in word:
            if letter in ascii_letters:
                text = text.replace(word, '')
            if letter in punctuation:
                text = text.replace(word, '')
            if letter not in [chr(i) for i in range(1920, 1970)]:
                text = text.replace(word, '')

    text = text.strip()

    return text


def find_sentence_with_word(text, word):
    # split into chucks of 500 words
    chunks = [text[i:i + 500] for i in range(0, len(text), 500)]
    sentences = [chunk for chunk in chunks if word in chunk]

    for sentence in sentences:
        return sentence

    return None
