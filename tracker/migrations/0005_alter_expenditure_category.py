# Generated by Django 4.1.5 on 2023-02-05 00:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0004_alter_expenditure_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expenditure',
            name='category',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='tracker.category'),
        ),
    ]
