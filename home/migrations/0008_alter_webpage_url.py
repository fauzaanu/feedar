# Generated by Django 5.0.1 on 2024-02-23 03:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0007_alter_searchresponse_unique_together'),
    ]

    operations = [
        migrations.AlterField(
            model_name='webpage',
            name='url',
            field=models.URLField(max_length=1000, unique=True),
        ),
    ]
