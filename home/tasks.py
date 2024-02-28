import logging
from datetime import datetime, timedelta
from string import ascii_letters, punctuation
from time import sleep

import requests
from bs4 import BeautifulSoup
from dhivehi_nlp import dictionary
from huey.contrib.djhuey import task

from home.helpers.api_calls import get_radheef_val
from home.helpers.db_process import process_meaning
from home.helpers.dhivehi_nlp_ext import get_part_of_speech
from home.helpers.formatting import preprocess_word
from home.helpers.search_process import find_sentence_with_word
from home.models import Word, Webpage, PartOfSpeech


@task()
def make_db():
    """
    Make the database
    """
    logging.error("Huey started")
    words = dictionary.get_wordlist()

    # in one query check if all words exist

    status = Word.objects.filter(word__in=words).values_list('word', flat=True)
    words = [word for word in words if word not in status]

    for word in words:
        if Word.objects.filter(word=word).exists():
            continue

        logging.error(f"Processing word: {word}")
        meaning_dnlp = dictionary.get_definition(preprocess_word(word))
        # meaning_radheef_api = get_radheef_val(word)

        part_of_speech = None
        if meaning_dnlp:
            try:
                part_of_speech = get_part_of_speech(word)
            except ValueError:
                part_of_speech = None

        if meaning_dnlp:
            word, _ = Word.objects.get_or_create(word=word)
            part_of_speech, _ = PartOfSpeech.objects.get_or_create(poc=part_of_speech)
            word.category.add(part_of_speech)
            process_meaning(meaning_dnlp, word, 'DhivehiNLP')
            logging.error(f"Meaning from dhivehiNLP added: {meaning_dnlp}")

        # Queue process_radheef_api task to run 5 minutes later
        eta = datetime.now() + timedelta(seconds=5)
        logging.error(f"Queueing radheef.mv for {word} at {eta}")
        process_radheef_api(word, part_of_speech)


def process_radheef_api(word, part_of_speech):
    """
    To not overload the radheef.mv server, we will process the words in batches and with a lot of delay
    """
    logging.error(f"Processing radheef.mv for {word}")
    meaning_radheef_api = get_radheef_val(word)
    word, _ = Word.objects.get_or_create(word=word, category=part_of_speech)
    process_meaning(meaning_radheef_api, word, 'radheef.mv')
    logging.error(f"Meaning from radheef.mv added: {meaning_radheef_api}")
    sleep(5)


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
