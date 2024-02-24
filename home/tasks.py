import logging
from datetime import date

from dhivehi_nlp import dictionary
from huey import crontab
from huey.contrib.djhuey import periodic_task, task

from home.helpers import google_custom_search, preprocess_word, process_meaning
from home.models import SearchResponse, Word, IndexQueue, Meaning


@task()
def make_db():
    """
    Make the database
    """
    logging.error("Huey started btw")
    words = dictionary.get_wordlist()
    for word in words:
        meaning = dictionary.get_definition(preprocess_word(word))
        if meaning:
            process_meaning(word, meaning)
            word, _ = Word.objects.get_or_create(word=word)
            meaning = str()
            for meaning in meaning:
                meaning += meaning + ', '

            meaning, _ = Meaning.objects.get_or_create(meaning=meaning, word=word)




# run every 15 minutes
@periodic_task(crontab(minute=0, hour=0))
def word_indexing_process():
    """
    Google Search engine has a free limit of 100 requests per day.
    There are 96 15-minute intervals in a day. So we can make 1 request every 15 minutes.
    By making 1 request every 15 minutes, we can make 96 requests in a day while also serving the users who are using the website.
    """
    # do we have enough requests left for today?
    todays_requests = SearchResponse.objects.filter(date=date.today()).count()
    if todays_requests >= 100:
        return

    # attempt to get a word to index
    words = IndexQueue.objects.filter(processed=False).limit(1)

    if not words:
        # find words that have not been indexed
        indexed_words = SearchResponse.objects.all().values_list("word", flat=True)
        words = Word.objects.exclude(id__in=indexed_words).limit(100)

        # add these words to the queue
        for word in words:
            IndexQueue.objects.create(word=word)

        # get 4 words to process
        words_from_que = IndexQueue.objects.filter(processed=False).limit(4)

        for word_from_que in words_from_que:
            word = word_from_que.word
            process_word = google_custom_search(word)

            if process_word:
                words_from_que.processed = True
                words_from_que.save()









