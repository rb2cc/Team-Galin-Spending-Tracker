# Generated by Django 4.1.5 on 2023-02-02 21:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0002_expenditure'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expenditure',
            name='image',
            field=models.ImageField(blank=True, upload_to='files/image'),
        ),
    ]
