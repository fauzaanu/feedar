# Generated by Django 5.0.1 on 2024-02-23 04:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0008_alter_webpage_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='searchresponse',
            name='date',
            field=models.DateField(auto_now_add=True, null=True),
        ),
    ]
