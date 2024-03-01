import logging
import random
from datetime import datetime, timedelta

import pytz
from dhivehi_nlp import dictionary
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.cache import cache_page

from home.helpers.db_process import process_meaning
from home.helpers.dhivehi_nlp_ext import process_related_words, get_part_of_speech
from home.helpers.formatting import remove_punctuation, is_dhivehi_word, preprocess_word
from home.helpers.search_process import google_custom_search
from home.models import Word, Webpage, SearchResponse, PartOfSpeech, SearchManager
from mysite.settings.base import SITE_VERSION


@cache_page(60 * 60 * 24 * 30,
            key_prefix=SITE_VERSION)
def home(request):
    return render(request, 'home/home.html')


@cache_page(60 * 60 * 24 * 30,
            key_prefix=SITE_VERSION)
def search_english(request):
    word = request.GET.get('word')

    if not word:
        return HttpResponse('Please enter a word')

    word = remove_punctuation(word)

    if is_dhivehi_word(word):
        return redirect('explore_word', word=word)
    else:
        return HttpResponse('This is not a dhivehi word')


def explore_word(request, word):
    if not word:
        return HttpResponse('Please enter a word')

    if not is_dhivehi_word(word):
        return HttpResponse('This is not a dhivehi word')

    meaning = dictionary.get_definition(preprocess_word(word))
    process_related_words(word)

    # Meaning want found, therefore, lets find related words
    if not meaning:
        context = {
            'related_only': True,
            'word': word,
            'r_words': Word.objects.filter(related_words__word=word),
        }
        return render(request, 'home/related.html', context)

    # Meaning was found, lets process it
    else:
        # removed process function : things could break
        on_demand_english_removal(word)

        # que maybe ongoing : to serve the user right away we need to process just this word
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

        if request.session.get('session_key'):
            del request.session['session_key']
        session_key = random.randint(100000, 999999)
        request.session['session_key'] = session_key
        SearchManager.objects.get_or_create(sezzon=session_key, duration=timedelta(seconds=60))

        # process the google search
        google_custom_search(word)

        context = {
            "session_key": session_key,
            'r_words': Word.objects.filter(related_words__word=word),
            'word': word,
            'words': Word.objects.filter(word=word),
            # 'search_result': Webpage.objects.filter(words__word=word, text_section__isnull=False),
        }
        return render(request, 'home/results.html', context)


def hx_load_web_data(request, word, session_key):
    if session_key and word:
        server_session_key = request.session.get('session_key')
        server_session_key = int(server_session_key)
        client_session_key = int(session_key)

        # get the session manager
        session_manager = SearchManager.objects.get(sezzon=server_session_key)

        session_started_on = session_manager.date_started
        session_duration = session_manager.duration

        current_time = datetime.now(pytz.timezone('Indian/Maldives'))
        current_duration = current_time - session_started_on

        print(f"Session started on: {session_started_on}")
        print(f"Session duration: {session_duration}")
        print(f"Current time: {current_time}")
        print(f"Current duration: {current_duration}")

        if current_duration > session_duration:
            return render(
                request,
                'home/hx_comps/final.html',
                {
                    'word': word,
                    'search_result': Webpage.objects.filter(words__word=word),
                }
            )

        if not session_key:
            return HttpResponse('not')

        word = remove_punctuation(word)
        if not is_dhivehi_word(word):
            return HttpResponse('This is not a dhivehi word')

        if server_session_key != client_session_key:
            return HttpResponse('Invalid session key')

        success = Webpage.objects.filter(words__word=word, status='success').count()
        failed = Webpage.objects.filter(words__word=word, status='failed').count()
        rest = Webpage.objects.filter(words__word=word).count()
        amount_of_results = success + failed

        print(success, failed, amount_of_results, rest)

        try:
            search = SearchResponse.objects.filter(word=Word.objects.get(word=word)).first()
        except SearchResponse.DoesNotExist:
            return HttpResponse('ERROR')

        amount_of_results_possible = search.link.count()
        print("Amount of results possible", amount_of_results_possible)

        if amount_of_results_possible == 0:
            return render(
                request,
                'home/hx_comps/final.html',
                {
                    'word': word,
                    'search_result': Webpage.objects.filter(words__word=word),
                }
            )

        if amount_of_results >= amount_of_results_possible:
            return render(
                request,
                'home/hx_comps/final.html',
                {
                    'word': word,
                    'search_result': Webpage.objects.filter(words__word=word),
                }
            )

        return render(
            request,
            'home/hx_comps/on_the_web.html',
            {
                'word': word,
                'session_key': server_session_key,
                'search_result': Webpage.objects.filter(words__word=word),
            }
        )


def hx_load_related(request):
