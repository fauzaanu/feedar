import random
from datetime import datetime, timedelta

import pytz
from dhivehi_nlp import dictionary
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.cache import cache_page

from home.helpers.dhivehi_nlp_ext import process_related_words
from home.helpers.english_removal import on_demand_english_removal
from home.helpers.formatting import remove_punctuation, is_dhivehi_word, preprocess_word
from home.models import Word, Webpage, SearchResponse, SearchManager
from home.tasks import google_custom_search
from mysite.settings.base import SITE_VERSION


@cache_page(60 * 60 * 24 * 30,
            key_prefix=SITE_VERSION)
def home(request):
    return render(request, 'home/home.html')


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

    on_demand_english_removal(word)

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
        # As we have completed the entire process we are sure that our database contains everything in the dictionary
        # uncomment this section if starting over todo: see this comment
        # que maybe ongoing : to serve the user right away we need to process just this word
        # logging.error(f"Processing word: {word}")
        # meaning_dnlp = dictionary.get_definition(preprocess_word(word))

        if request.session.get('session_key'):
            del request.session['session_key']
        session_key = random.randint(100000, 999999)
        request.session['session_key'] = session_key
        SearchManager.objects.get_or_create(sezzon=session_key, duration=timedelta(seconds=60))

        # a huey task : this wont delay the response
        google_custom_search(word)

        context = {
            "session_key": session_key,
            'word': word,
            'words': Word.objects.filter(word=word),
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

        if current_duration > session_duration:
            return render(
                request,
                'home/hx_comps/on_the_web/final.html',
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
        amount_of_results = success + failed

        try:
            search = SearchResponse.objects.filter(word=Word.objects.get(word=word)).first()
            amount_of_results_possible = search.link.count()

            # if no results are possible send the final response
            # if we have more than 10 results, send the final response
            if amount_of_results_possible == 0 or amount_of_results >= amount_of_results_possible:
                return render(
                    request,
                    'home/hx_comps/on_the_web/final.html',
                    {
                        'word': word,
                        'search_result': Webpage.objects.filter(words__word=word),
                    }
                )

            return render(
                request,
                'home/hx_comps/on_the_web/on_the_web.html',
                {
                    'word': word,
                    'session_key': server_session_key,
                    'search_result': Webpage.objects.filter(words__word=word),
                }
            )
        except SearchResponse.DoesNotExist:
            return HttpResponse('ERROR')


def hx_load_related(request, word, session_key):
    if session_key and word:
        server_session_key = request.session.get('session_key')
        server_session_key = int(server_session_key)
        client_session_key = int(session_key)

        if client_session_key != server_session_key:
            return HttpResponse('Invalid session key')

        word = remove_punctuation(word)

        if not is_dhivehi_word(word):
            return HttpResponse('This is not a dhivehi word')

        return render(
            request,
            'home/hx_comps/related_words/final.html',
            {
                'r_words': Word.objects.filter(related_words__word=word),
            }
        )
