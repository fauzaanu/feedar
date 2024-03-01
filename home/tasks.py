import logging
import random
from datetime import date
from string import ascii_letters, punctuation
from time import sleep

import requests
from bs4 import BeautifulSoup
from dhivehi_nlp import dictionary
from huey import crontab
from huey.contrib.djhuey import task, periodic_task

from home.helpers.api_calls import get_radheef_val, google_custom_search_api
from home.helpers.db_process import process_meaning
from home.helpers.dhivehi_nlp_ext import get_part_of_speech
from home.helpers.formatting import preprocess_word, remove_all_english
from home.helpers.mynameisroot import hey_root
from home.helpers.search_process import find_sentence_with_word
from home.models import Word, Webpage, PartOfSpeech, SearchResponse


@periodic_task(crontab(minute='*/60'))
def make_db():
    """
    Make the database
    """
    logging.error("Huey started")
    words = dictionary.get_wordlist()
    words_in_db = Word.objects.all().values_list('word', flat=True)

    words = list(set(words) - set(words_in_db))
    # take 1000 random words or less
    words = random.sample(words, 1000) if len(words) > 1000 else words

    total_words = len(words)
    skipped_words = int()
    processed_words = int()
    for word in words:
        if Word.objects.filter(word=word).exists():
            skipped_words += 1
            continue

        logging.error(f"Processing word: {word}")
        meaning_dnlp = dictionary.get_definition(preprocess_word(word))

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

        process_radheef_api(word)
        processed_words += 1

    msg = f"Total words: {total_words}, Processed words: {processed_words}, Skipped words: {skipped_words}"
    hey_root(msg)
    logging.error(msg)


@task()
def google_custom_search(word):
    word_obj, _ = Word.objects.get_or_create(word=word)

    if Webpage.objects.filter(words__word=word).exists():
        all_pages = Webpage.objects.filter(words__word=word)
        for page in all_pages:
            if page.text_section:
                text = remove_all_english(page.text_section)

                if text.isspace():
                    page.status = 'failed'
                    page.save()
                    return None

                page.text_section = text
                page.save()
        return None

    # check if our daily limit is above 100
    current_requests = SearchResponse.objects.filter(date=date.today()).count()
    if current_requests > 100:
        return None

    response = google_custom_search_api(word)
    response_json = response.json()
    amount = response_json['searchInformation']['totalResults']

    if amount == '0':
        return None

    items = response.json()['items']
    urls = [item['link'] for item in items]

    search = SearchResponse.objects.create(word=word_obj)

    for url in urls:
        search.link.add(Webpage.objects.get_or_create(url=url)[0])
        process_weblink(url, word)
    return True


def process_radheef_api(word):
    """
    To not overload the radheef.mv server, we will process the words in batches and with a lot of delay
    """
    logging.error(f"Processing radheef.mv for {word}")
    meaning_radheef_api = get_radheef_val(word)
    word, _ = Word.objects.get_or_create(word=word)
    process_meaning(meaning_radheef_api, word, 'radheef.mv')
    logging.error(f"Meaning from radheef.mv added: {meaning_radheef_api}")
    sleep(0.1)


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
