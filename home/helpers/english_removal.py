from home.helpers.formatting import is_dhivehi_word
from home.models import Webpage


def on_demand_english_removal(word):
    pages = Webpage.objects.filter(words__word=word, text_section__isnull=False)
    for page in pages:
        text = page.text_section
        if page.text_section:

            # remove english words
            for word in text.split():
                if not is_dhivehi_word(word):
                    text = text.replace(word, '')

            page.text_section = text
            page.save()
    return True
