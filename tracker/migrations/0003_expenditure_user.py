# Generated by Django 4.1.5 on 2023-02-04 23:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0002_remove_expenditure_user_expenditure_category_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='expenditure',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
