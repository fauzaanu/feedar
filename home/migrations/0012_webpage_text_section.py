# Generated by Django 5.0.1 on 2024-02-24 02:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0011_webpage_text_content'),
    ]

    operations = [
        migrations.AddField(
            model_name='webpage',
            name='text_section',
            field=models.TextField(blank=True, null=True),
        ),
    ]
