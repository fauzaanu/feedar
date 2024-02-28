from django.db import models


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
        return self.title

    def get_domain(self):
        return self.url.split('/')[2]


class SearchResponse(models.Model):
    date = models.DateField(auto_now_add=True, blank=True, null=True)
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    link = models.ManyToManyField(Webpage)

    def __str__(self):
        return f"{self.word} - {self.webpage} - {self.count}"


class IndexQueue(models.Model):
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
