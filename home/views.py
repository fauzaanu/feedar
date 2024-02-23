import json
import os
from string import ascii_letters, digits, punctuation

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.cache import cache_page
from dotenv import load_dotenv

from home.helpers import is_dhivehi_word, remove_punctuation, google_custom_search, get_related_words
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
    PAGE_TITLE = "Dhivehi Radheef for " + word + " | Radheefu.com"

    if not word:
        return HttpResponse('Please enter a word')

    if is_dhivehi_word(word):
        word = word.lower()
        word = remove_punctuation(word)
        word = stemmer.stem(word)

        if type(word) == list:
            word = word[0]

        meaning = dictionary.get_definition(word)

        if not meaning:
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

                context = {
                    'related_only': True,
                    'word': word,
                    'words': Word.objects.filter(related_words__word=word),
                    'title': PAGE_TITLE
                }
                return render(request, 'home/search_english.html', context)

        else:
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

                        meaning_item = remove_punctuation(meaning_item)

                        if meaning_item:
                            related_word, _ = Word.objects.get_or_create(word=meaning_item)
                            word_obj.related_words.add(related_word)
                            word_obj.save()

                            meaning = dictionary.get_definition(meaning_item)
                            for mean in meaning:
                                mean = remove_punctuation(mean)
                                if mean:
                                    Meaning.objects.get_or_create(meaning=mean, word=related_word)

                        # Get more words
                        words = tokenizer.word_tokenize(meaning_item)
                        for wrd in words:
                            mn = dictionary.get_definition(wrd)

                            if mn:
                                related_word, _ = Word.objects.get_or_create(word=wrd)
                                word_obj.related_words.add(related_word)
                                word_obj.save()
                                for definition in mn:
                                    definition = remove_punctuation(definition)
                                    if definition:
                                        Meaning.objects.get_or_create(meaning=definition, word=related_word)

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

                context = {
                    'title': PAGE_TITLE,
                    'words': Word.objects.filter(word=word),
                    'search_result': Webpage.objects.filter(words__word=word)
                }
                return render(request, 'home/search_english.html', context)
