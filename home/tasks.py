import logging
from string import ascii_letters, punctuation

import requests
from bs4 import BeautifulSoup
from dhivehi_nlp import dictionary
from huey.contrib.djhuey import task

from home.helpers import preprocess_word, process_meaning, find_sentence_with_word
from home.models import Word, Meaning, Webpage


@task()
def make_db():
    """
    Make the database
    """
    logging.error("Huey started btw")
    words = dictionary.get_wordlist()
    for word in words:
        meaning = dictionary.get_definition(preprocess_word(word))
        if meaning:
            process_meaning(word, meaning)
            word, _ = Word.objects.get_or_create(word=word)
            meaning = str()
            for meaning in meaning:
                meaning += meaning + ', '

            meaning, _ = Meaning.objects.get_or_create(meaning=meaning, word=word)


def extract_text_from_html(url):
    response = requests.get(url)
    html_content = response.content

    soup = BeautifulSoup(html_content, 'html.parser', from_encoding="utf-8")

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


@task()
def process_weblink(url, word):

    word_obj, _ = Word.objects.get_or_create(word=word)

    page, _ = Webpage.objects.get_or_create(url=url)

    try:

        if page.status == 'failed':
            logging.error(f"Page {url} failed")
            return None

        page.words.add(word_obj)

        page.text_content = extract_text_from_html(url)

        sentence = find_sentence_with_word(page.text_content, word)

        if sentence:
            if not str(sentence).isspace():
                page.status = 'success'
                page.text_section = only_dhivehi_allowed(sentence)
                page.save()
            else:
                page.status = 'failed'
                page.save()
        else:
            page.status = 'failed'
            page.save()
    except Exception as e:
        logging.error(f"Error: {e}")
        page.status = 'failed'
        page.save()
        return None


def only_dhivehi_allowed(text):
    """
    Remove english words from text
    """
    for word in text.split():
        for letter in word:
            if letter in ascii_letters:
                text = text.replace(word, '')
            if letter in punctuation:
                text = text.replace(word, '')
            if letter not in [chr(i) for i in range(1920, 1970)]:
                text = text.replace(word, '')

    return text