import json
import os
from string import ascii_letters, digits, punctuation

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.cache import cache_page
from dotenv import load_dotenv

from home.helpers import is_dhivehi_word, remove_punctuation, google_custom_search, get_related_words, \
    process_related_words, process_meaning
from home.models import Word, Meaning, SearchResponse, Webpage
from mysite.settings.base import SITE_VERSION
from dhivehi_nlp import dictionary, stemmer, tokenizer


# 30 days cache, example using site version to invalidate cache (increment to
# invalidate)
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


@cache_page(60 * 60 * 24 * 30,
            key_prefix=SITE_VERSION)
def explore_word(request, word):
    page_title = "Dhivehi Radheef for " + word + " | Radheefu.com"

    if not word:
        return HttpResponse('Please enter a word')

    if not is_dhivehi_word(word):
        return HttpResponse('This is not a dhivehi word')

    word = word.lower()
    word = remove_punctuation(word)
    word = stemmer.stem(word)

    if type(word) == list:
        word = word[0]

    meaning = dictionary.get_definition(word)

    # Meaning want found, therefore, lets find related words
    if not meaning:
        process_related_words(word)

        context = {
            'related_only': True,
            'word': word,
            'words': Word.objects.filter(related_words__word=word),
            'p_title': page_title
        }
        return render(request, 'home/search_english.html', context)

    # Meaning was found, lets process it
    else:
        process_meaning(word, meaning)
        context = {
            'p_title': page_title,
            'words': Word.objects.filter(word=word),
            'search_result': Webpage.objects.filter(words__word=word)
        }
        return render(request, 'home/search_english.html', context)
