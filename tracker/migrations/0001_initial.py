# Generated by Django 4.1.5 on 2023-03-15 20:33

from decimal import Decimal
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django_resized.forms
import tinymce.models
import tracker.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('email', models.EmailField(max_length=50, unique=True)),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('username', models.CharField(blank=True, max_length=50, null=True, unique=True)),
                ('trees', models.IntegerField(default=0)),
            ],
            options={
                'abstract': False,
            },
            managers=[
                ('objects', tracker.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Achievement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('criteria', models.TextField()),
                ('badge', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('week_limit', models.PositiveIntegerField()),
                ('is_global', models.BooleanField(default=False)),
                ('is_overall', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='Challenge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('points', models.IntegerField()),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('media', models.ImageField(blank=True, upload_to='images')),
            ],
        ),
        migrations.CreateModel(
            name='Forum_Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
                ('slug', models.SlugField()),
                ('description', models.TextField(default='description')),
            ],
            options={
                'verbose_name_plural': 'forum_categories',
            },
        ),
        migrations.CreateModel(
            name='Level',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('required_points', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='UserLevel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('points', models.PositiveIntegerField()),
                ('date_reached', models.DateTimeField(auto_now=True)),
                ('level', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tracker.level')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Tree',
            fields=[
                ('tree_id', models.AutoField(primary_key=True, serialize=False)),
                ('x_position', models.IntegerField()),
                ('y_position', models.IntegerField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Reply',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('media', models.ImageField(blank=True, upload_to='images')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'replies',
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('forget_password_token', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=400)),
                ('slug', models.SlugField(blank=True, max_length=400, unique=True)),
                ('content', tinymce.models.HTMLField()),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('approved', models.BooleanField(default=True)),
                ('media', models.ImageField(blank=True, upload_to='images')),
                ('comments', models.ManyToManyField(blank=True, to='tracker.comment')),
                ('forum_categories', models.ManyToManyField(to='tracker.forum_category')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Expenditure',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=20)),
                ('description', models.CharField(max_length=280)),
                ('image', models.ImageField(blank=True, upload_to='images')),
                ('expense', models.DecimalField(decimal_places=2, max_digits=20, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_binned', models.BooleanField(default=False)),
                ('category', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='tracker.category')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='comment',
            name='replies',
            field=models.ManyToManyField(blank=True, to='tracker.reply'),
        ),
        migrations.AddField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Avatar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_name', models.CharField(max_length=255)),
                ('current_template', models.CharField(max_length=255)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fullname', models.CharField(blank=True, max_length=40)),
                ('slug', models.SlugField(blank=True, max_length=400, unique=True)),
                ('bio', tinymce.models.HTMLField()),
                ('points', models.IntegerField(default=0)),
                ('profile_pic', django_resized.forms.ResizedImageField(blank=True, crop=None, default=None, force_format=None, keep_meta=True, null=True, quality=100, scale=None, size=[50, 80], upload_to='authors')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('points', models.IntegerField(default=0)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='available_categories',
            field=models.ManyToManyField(related_name='users', to='tracker.category'),
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions'),
        ),
        migrations.CreateModel(
            name='UserChallenge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_entered', models.DateTimeField(auto_now=True)),
                ('date_completed', models.DateTimeField(blank=True, null=True)),
                ('challenge', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tracker.challenge')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'challenge')},
            },
        ),
        migrations.CreateModel(
            name='UserAchievement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_earned', models.DateTimeField(auto_now=True)),
                ('achievement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tracker.achievement')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'achievement')},
            },
        ),
    ]
