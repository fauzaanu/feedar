import json
import os
from datetime import date
from string import ascii_letters, punctuation

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
    search_result = google_custom_search(word)
    if search_result:
        search_result = search_result.response

        # search result has a { } json object
        search_result = json.loads(search_result)

        for item in search_result['items']:
            link = item['link']
            title = item['title']

            # find a .jpg or .png image from the item string
            item_str = str(item)
            image_link = None
            begins_with = ['http://', 'https://']
            ends_with = ['.jpg', '.png', '.jpeg', '.webp']

            # find the first image in the item string
            for image_end in ends_with:
                imgage = item_str.find(image_end)
                if imgage != -1:
                    # find the first http or https before the image
                    for start in begins_with:
                        start_index = item_str.rfind(start, 0, imgage)
                        if start_index != -1:
                            image_link = item_str[start_index:imgage + len(image_end)]
                            break

            image_link = image_link if image_link else None
            page, _ = Webpage.objects.get_or_create(url=link, title=title, image_link=image_link)
            page.words.add(word_obj)

    return True


def preprocess_word(word):
    word = word.lower()
    word = remove_punctuation(word)
    word = stemmer.stem(word)

    if type(word) == list:
        word = word[0]

    return word


from bs4 import BeautifulSoup


def extract_text_from_html(url):
    response = requests.get(url)
    html_content = response.content

    soup = BeautifulSoup(html_content, 'html.parser')

    # Remove script tags
    for script in soup(['script', 'style']):
        script.extract()

    # Get all text
    text = soup.get_text()

    return text


def find_sentence_with_word(text, word):
    sentences = text.split('.')
    # print(sentences)
    for sentence in sentences:
        if word in sentence:
            return sentence
    return None


def null_characters(word):
    return word.replace('\x00', '')


def process_textual_content(request, word):
    # process textual content
    websites = Webpage.objects.filter(words__word=word)
    for site in websites:
        if site.text_section:
            continue

        if not site.text_content:
            # get the text content from the website
            text = extract_text_from_html(site.url)
            site.text_content = null_characters(text)
            site.save()

        else:
            sentence = find_sentence_with_word(site.text_content, word)
            if sentence:
                site.text_section = null_characters(sentence)
                site.save()
            else:
                site.delete()
                continue
