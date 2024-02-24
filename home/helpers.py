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
            page.text_section = sentence
        page.save()
    return True


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


def process_related_words(word):
    """
    Process related words for a given word
    """
    related_words = get_related_words(filter=word)
    if related_words:
        q_word, _ = Word.objects.get_or_create(word=word)
        for rel_word in related_words:
            rel_word = remove_punctuation(rel_word)
            if rel_word:
                meaning = dictionary.get_definition(rel_word)
                if meaning:
                    word_obj, _ = Word.objects.get_or_create(word=rel_word)
                    q_word.related_words.add(word_obj)
                    for mean in meaning:
                        mean = remove_punctuation(mean)
                        if mean:
                            Meaning.objects.get_or_create(meaning=mean, word=word_obj)

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

    # ensure that the text does not have bad characters
    # good for postgresql
    text = text.encode('utf-8').decode('utf-8')

    # remove english words
    for word in text.split():
        if not is_dhivehi_word(word):
            text = text.replace(word, '')

    return text


def find_sentence_with_word(text, word):
    sentences = text.split('.')
    # print(sentences)
    for sentence in sentences:
        if word in sentence:

            # remove english words
            for word in sentence.split():
                for letter in word:
                    if letter in ascii_letters:
                        sentence = sentence.replace(word, '')

            # shorten the sentence by stripping if too long
            word_length = len(word)

            if len(sentence) > 20 * word_length:
                # find the position of the word
                position = sentence.find(word)
                # add 10 * word_length to the position and subtract 10 * word_length from the position
                sentence = sentence[position - 10 * word_length:position + 10 * word_length]
            return sentence

    return None
