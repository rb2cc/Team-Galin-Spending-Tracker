# Generated by Django 4.1.5 on 2023-03-23 15:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='has_email_sent',
            field=models.BooleanField(default=False),
        ),
    ]