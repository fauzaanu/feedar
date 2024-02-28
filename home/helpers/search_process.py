from datetime import date

from home.helpers.api_calls import google_custom_search_api
from home.helpers.formatting import remove_all_english
from home.models import Word, Webpage, SearchResponse


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
        from home.tasks import process_weblink
        process_weblink(url, word)
    return True

def find_sentence_with_word(text, word):
    # split into chucks of 500 words
    chunks = [text[i:i + 250] for i in range(0, len(text), 250)]
    sentences = [chunk for chunk in chunks if word in chunk]

    for sentence in sentences:
        return sentence

    return None
