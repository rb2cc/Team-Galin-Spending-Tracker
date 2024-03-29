# Generated by Django 4.1.5 on 2023-03-24 16:00

from django.db import migrations, models
import tracker.models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='slug',
            field=models.SlugField(default=tracker.models.random_slug_number, max_length=400, unique=True),
        ),
    ]
