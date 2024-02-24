from django.db import models


# Create your models here.


class Word(models.Model):
    word = models.CharField(max_length=100, unique=True)
    related_words = models.ManyToManyField('self', blank=True)

    def __str__(self):
        return self.word


class Meaning(models.Model):
    meaning = models.CharField(max_length=1000)
    word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name='meanings')

    def __str__(self):
        return self.meaning


class Webpage(models.Model):
    """
    We store the url, of the webpage that mentions the word
    """
    url = models.URLField(unique=True, max_length=1000)
    title = models.CharField(max_length=100)
    words = models.ManyToManyField(Word)
    image_link = models.URLField(blank=True, null=True)
    text_content = models.TextField(blank=True, null=True)
    text_section = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title

    def get_domain(self):
        return self.url.split('/')[2]


class SearchResponse(models.Model):
    date = models.DateField(auto_now_add=True, blank=True, null=True)
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    response = models.TextField(db_index=False)

    def __str__(self):
        return f"{self.word} - {self.webpage} - {self.count}"


class IndexQueue(models.Model):
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)