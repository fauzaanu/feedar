from dhivehi_nlp import dictionary
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.cache import cache_page

from home.helpers import is_dhivehi_word, remove_punctuation, process_related_words, process_meaning, preprocess_word, \
    extract_text_from_html, find_sentence_with_word
from home.models import Word, Webpage
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


@cache_page(60 * 60 * 24 * 30,
            key_prefix=SITE_VERSION)
def explore_word(request, word):
    if not word:
        return HttpResponse('Please enter a word')

    if not is_dhivehi_word(word):
        return HttpResponse('This is not a dhivehi word')

    meaning = dictionary.get_definition(preprocess_word(word))

    # Meaning want found, therefore, lets find related words
    if not meaning:
        process_related_words(word)

        context = {
            'related_only': True,
            'word': word,
            'words': Word.objects.filter(related_words__word=word),
        }
        return render(request, 'home/results.html', context)

    # Meaning was found, lets process it
    else:
        process_meaning(word, meaning)

        # process textual content
        websites = Webpage.objects.filter(words__word=word)
        for site in websites:
            if site.text_section:
                continue

            if site.text_content:
                sentence = find_sentence_with_word(site.text_content, word)
                if sentence:
                    site.text_section = sentence
                    site.save()
                else:
                    site.delete()
                    continue

            if not site.text_content:
                # get the text content from the website
                text = extract_text_from_html(site.url)
                # print(text)
                site.text_content = text
                site.save()

                # try to find the word in the text content

        context = {
            'word': word,
            'words': Word.objects.filter(word=word),
            'search_result': Webpage.objects.filter(words__word=word, text_section__isnull=False),
        }
        return render(request, 'home/results.html', context)
