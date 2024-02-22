from string import ascii_letters, digits, punctuation

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.cache import cache_page

from home.models import Word, Meaning
from mysite.settings.base import SITE_VERSION
from dhivehi_nlp import dictionary, stemmer, tokenizer


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
    def get_radheef_val(word):
        import requests
        url = "https://www.radheef.mv/api/basfoiy/search_word"

        # generated code from insomnia

        payload = f"-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"searchText\"\r\n\r\n{word}\r\n-----011000010111000001101001--\r\n"
        headers = {
            "cookie": "ci_session=e2cals79khosk6e9nbcubpkednnl5rq9",
            "Content-Type": "multipart/form-data; boundary=---011000010111000001101001"
        }

        payload = payload.encode()
        response = requests.request("POST", url, data=payload, headers=headers)
        with open('response.json', 'w') as f:
            f.write(response.text)

        if response.json()['data']:
            return [resp for resp in response.json()['data']]
        else:
            return None

    # is it a dhivehi word or not? - todo:refactor later
    if not word:
        return render(request, 'home/search_english.html', {'meaning': 'Please enter a word'})
    for letter in word:
        if letter in ascii_letters:
            return render(request, 'home/search_english.html', {'meaning': 'This is not a Dhivehi word'})

    word = word.lower()
    # remove punctuation and spaces
    word = ''.join([char for char in word if char not in punctuation + digits])

    # stemmer.stem
    word = stemmer.stem(word)

    if type(word) == list:
        word = word[0]

    meaning = dictionary.get_definition(word)

    if not meaning:
        # # query radheef for meaning
        # meaning = get_radheef_val(word)

        if not meaning:
            related_words = dictionary.get_related_words(filter=word)

            if related_words:

                q_word, _ = Word.objects.get_or_create(word=word)

                for rel_word in related_words:
                    rel_word = ''.join([char for char in rel_word if char not in punctuation + digits])
                    if rel_word:
                        meaning = dictionary.get_definition(rel_word)
                        if meaning:
                            word_obj, _ = Word.objects.get_or_create(word=rel_word)
                            q_word.related_words.add(word_obj)
                            for mean in meaning:
                                # remove punctuation and spaces
                                mean = ''.join([char for char in mean if char not in punctuation + digits])
                                if mean:
                                    Meaning.objects.get_or_create(meaning=mean, word=word_obj)

                context = {
                    'words': Word.objects.filter(related_words__word=word),
                }
                return render(request, 'home/search_english.html', context)

    if meaning:
        word_obj, _ = Word.objects.get_or_create(word=word)

        for mean in meaning:
            # remove punctuation and spaces
            mean = ''.join([char for char in mean if char not in punctuation + digits])
            if mean:
                Meaning.objects.get_or_create(meaning=mean, word=word_obj)

        word_len = len(word)
        for i in range(word_len):
            wrd = word[:word_len - i]
            meaning = dictionary.get_definition(wrd)
            if meaning:
                related_word, _ = Word.objects.get_or_create(word=wrd)
                word_obj.related_words.add(related_word)
                word_obj.save()

                for meaning_item in meaning:

                    meaning_item = ''.join([char for char in meaning_item if char not in punctuation + digits])
                    if meaning_item:
                        Meaning.objects.get_or_create(meaning=meaning_item, word=related_word)

                    meaning_item = ''.join([char for char in meaning_item if char not in punctuation + digits])
                    if meaning_item:
                        related_word, _ = Word.objects.get_or_create(word=meaning_item)
                        word_obj.related_words.add(related_word)
                        word_obj.save()

                        meaning = dictionary.get_definition(meaning_item)
                        for mean in meaning:
                            # remove punctuation and spaces
                            mean = ''.join([char for char in mean if char not in punctuation + digits])
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
                                # remove punctuation and spaces
                                definition = ''.join([char for char in definition if char not in punctuation + digits])
                                if definition:
                                    Meaning.objects.get_or_create(meaning=definition, word=related_word)

        context = {
            'words': Word.objects.filter(word=word),
        }
        return render(request, 'home/search_english.html', context)
    else:
        # query radheef for meaning
        return HttpResponse('No meaning found for this word')



def word_usage_on_the_web(request,word):
    # GET https://www.googleapis.com/customsearch/v1?key=[GOOGLE_SEARCH_API_KEY]&cx=[CX]&q=[word]&exactTerms=[word]
    pass
