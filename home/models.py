import os
import sqlite3

from django.db import models

from mysite.settings.base import BASE_DIR


# Create your models here.
class PartOfSpeech(models.Model):
    poc = models.CharField(max_length=100,
                           choices=[
                               ('nan', 'nan'),
                               ('kan', 'kan'),
                               ('nan ithuru', 'nan_ithuru'),
                               ('kan ithuru', 'kan_ithuru'),
                               ('masdharu', 'masdharu'),
                               ('nan ithuruge nan', 'nan_ithuruge_nan'),
                               ('ithuru', 'ithuru'),
                               ('akuru', 'akuru')
                           ],
                           blank=True, null=True)


class Word(models.Model):
    word = models.CharField(max_length=100, unique=True)
    related_words = models.ManyToManyField('self', blank=True)
    category = models.ManyToManyField(PartOfSpeech)

    def __str__(self):
        return self.word

    def get_latin(self):
        try:
            latin_db = os.path.join(BASE_DIR, 'home', 'helpers', 'thaana_to_latin', 'data', 'latin.sqlite3')
            con = sqlite3.connect(latin_db)
            cursor = con.cursor()
            query = f"SELECT latin FROM words WHERE word='{self.word}'"
            cursor.execute(query)
            result = cursor.fetchone()
            con.close()
            if result:
                return result[0]
            else:
                return None
        except Exception as e:
            return None


class Meaning(models.Model):
    meaning = models.CharField(max_length=1000)
    word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name='meanings')
    source = models.CharField(choices=[
        ("DhivehiNLP", "Dhivehi_NLP"),
        ("radheef.mv", "radheef_mv"),
    ]
        , max_length=100, default='DhivehiNLP')

    def __str__(self):
        return self.meaning

    def get_part_of_speech(self):

        poc_dhivehi = {
            'nan': 'ނަން',
            'kan': 'ކަން',
            'nan ithuru': 'ނަންއިތުރު',
            'kan ithuru': 'ކަންއިތުރު',
            'masdharu': 'މަސްދަރު',
            'nan ithuruge nan': 'ނަންއިތުރުގެ ނަން',
            'ithuru': 'އިތުރު',
            'akuru': 'އަކުރު'
        }

        display_string = ''
        categories = self.word.category.all()
        for category in categories:
            poc = category.poc

            if display_string != '':
                display_string += ', '

            if poc in poc_dhivehi:
                display_string += poc_dhivehi[poc]

        return display_string

    def get_data_source(self):

        if self.source == 'DhivehiNLP':
            return 'Dhivehi NLP ' + 'ގައި ބޭނުންކުރެވިފައިވާ ޑޭޓާބޭސްއިން'

        elif self.source == 'radheef.mv':
            return 'radheef.mv ' + 'ގައި ބޭނުންކުރެވިފައިވާ އޭޕީއައި އިން'


class Webpage(models.Model):
    """
    We store the url, of the webpage that mentions the word
    """
    url = models.URLField(unique=True, max_length=1000)
    words = models.ManyToManyField(Word)
    text_content = models.TextField(blank=True, null=True)
    text_section = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=100, default='started')

    def __str__(self):
        return self.url

    def get_domain(self):
        return self.url.split('/')[2]


class SearchResponse(models.Model):
    date = models.DateField(auto_now_add=True, blank=True, null=True)
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    link = models.ManyToManyField(Webpage)

    def __str__(self):
        return self.word.word


class IndexQueue(models.Model):
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)


class SearchManager(models.Model):
    """
    A search could just fail. so lets manage it properly
    """
    sezzon = models.CharField(max_length=100, blank=True, null=True,
                              unique=True)  # not session because i dont want to take a risk with the name session
    date_started = models.DateTimeField(auto_now_add=True)
    duration = models.DurationField(blank=True, null=True)

    def __str__(self):
        return self.sezzon
