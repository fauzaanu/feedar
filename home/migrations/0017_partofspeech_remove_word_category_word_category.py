# Generated by Django 5.0.1 on 2024-02-28 02:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0016_meaning_source_word_category'),
    ]

    operations = [
        migrations.CreateModel(
            name='PartOfSpeech',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('poc', models.CharField(blank=True, choices=[('nan', 'nan'), ('kan', 'kan'), ('nan ithuru', 'nan_ithuru'), ('kan ithuru', 'kan_ithuru'), ('masdharu', 'masdharu'), ('nan ithuruge nan', 'nan_ithuruge_nan'), ('ithuru', 'ithuru'), ('akuru', 'akuru')], max_length=100, null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='word',
            name='category',
        ),
        migrations.AddField(
            model_name='word',
            name='category',
            field=models.ManyToManyField(to='home.partofspeech'),
        ),
    ]
