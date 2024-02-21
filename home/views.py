from string import ascii_letters, digits, punctuation

from django.shortcuts import render
from django.views.decorators.cache import cache_page

from mysite.settings.base import SITE_VERSION
from dhivehi_nlp import dictionary


# 30 days cache, example using site version to invalidate cache (increment to
# invalidate)
@cache_page(60 * 60 * 24 * 30,
            key_prefix=SITE_VERSION)
def home(request):
    return render(request, 'home/home.html')


def search_english(request):
    word = request.POST.get('word')

    # remove punctuation and spaces
    word = ''.join([char for char in word if char not in punctuation + digits])

    # is it a dhivehi word or not?
    if not word:
        return render(request, 'home/search_english.html', {'meaning': 'Please enter a word'})
    for letter in word:
        if letter in ascii_letters:
            return render(request, 'home/search_english.html', {'meaning': 'This is not a Dhivehi word'})

    word = word.lower()
    meaning = dictionary.get_definition(word)

    context = {
        'word': word,
        'meaning': meaning,
    }

    return render(request, 'home/search_english.html', context)


def explore_word(request, word):
    # is it a dhivehi word or not? - todo:refactor later
    if not word:
        return render(request, 'home/search_english.html', {'meaning': 'Please enter a word'})
    for letter in word:
        if letter in ascii_letters:
            return render(request, 'home/search_english.html', {'meaning': 'This is not a Dhivehi word'})

    word = word.lower()
    # remove punctuation and spaces
    word = ''.join([char for char in word if char not in punctuation + digits])

    meaning = dictionary.get_definition(word)

    context = {
        'word': word,
        'meaning': meaning,
    }
    return render(request, 'home/search_english.html', context)
