from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin, User
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from personal_spending_tracker import settings
from decimal import Decimal
from django.utils import timezone
from taggit.managers import TaggableManager
from django.shortcuts import reverse
from django.utils.text import slugify
from django.contrib.contenttypes.fields import GenericRelation
from hitcount.models import HitCountMixin, HitCount
from django_resized import ResizedImageField
from tinymce.models import HTMLField
from django.contrib.auth import get_user_model

# Create your models here.


class UserManager(BaseUserManager):
    """Manage user model objects"""

    use_in_migrations = True


    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_staff', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """User model used for authentication"""

    email = models.EmailField(
        unique=True,
        max_length=50,
        blank=False,
    )
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    available_categories = models.ManyToManyField('Category', symmetrical = False, related_name = 'users')
    username = models.CharField(max_length=50, blank=True)
    points = models.IntegerField(default=0)
    trees = models.IntegerField(default=0)

    objects = UserManager()
    USERNAME_FIELD = 'email'

    @property
    def num_posts(self):
        return Post.objects.filter(user=self).count()


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    forget_password_token = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email

    def _add_category(self, category):
        self.available_categories.add(category)

    def _remove_category(self, category):
        self.available_categories.remove(category)

class Category(models.Model):
    """Categories used for classifying expenditure"""

    name = models.CharField(max_length=50, blank=False)
    week_limit = models.PositiveIntegerField()
    is_global = models.BooleanField(default=False)
    is_overall = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

class Expenditure(models.Model):
    """Expenditure model for user spending"""

    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    title = models.CharField(max_length=20, blank=False)
    description = models.CharField(max_length=280, blank=False)
    image = models.ImageField(editable=True, upload_to='images', blank=True)
    expense = models.DecimalField(max_digits=20, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], null=False)
    date_created = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    is_binned = models.BooleanField(default=False, null=False);

class Challenge(models.Model):
    """Challenge model for storing information about challenges."""
    name = models.CharField(max_length=255)
    description = models.TextField()
    points = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()

    def clean(self):
        if self.end_date <= self.start_date:
            raise ValidationError("End date should be after start date.")

class UserChallenge(models.Model):
    """User challenge model to keep track of which user is participating in which challenge."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    date_entered = models.DateTimeField(auto_now=True)
    date_completed = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'challenge')

class Achievement(models.Model):
    """Achievement model for storing information about achievements."""
    name = models.CharField(max_length=100)
    description = models.TextField()
    criteria = models.TextField()
    badge = models.CharField(max_length=255)

class UserAchievement(models.Model):
    """User achievement model to keep track of which user received which achievement."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    date_earned = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'achievement')

class Level(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    required_points = models.PositiveIntegerField()

class UserLevel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    points = models.PositiveIntegerField()
    date_reached = models.DateTimeField(auto_now=True)

class Activity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    time = models.DateTimeField(auto_now_add=True)
    points = models.IntegerField(default=0)

# Creation of forums models

User = get_user_model()

class Author(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fullname = models.CharField(max_length=40, blank=True)
    slug = models.SlugField(max_length=400, unique=True, blank=True)
    bio = HTMLField()
    points = models.IntegerField(default=0)
    profile_pic = ResizedImageField(size=[50, 80], quality=100, upload_to="authors", default=None, null=True, blank=True)

    def __str__(self):
        return self.fullname

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.fullname)
        super(Author, self).save(*args, **kwargs)

class Forum_Category(models.Model):
    title = models.CharField(max_length=50)
    slug = models.SlugField()
    description = models.TextField(default="description")

    class Meta:
        verbose_name_plural = "forum_categories"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Forum_Category, self).save(*args, **kwargs)

    def get_url(self):
        return reverse("posts", kwargs= {
            "slug":self.slug
        })

    @property
    def num_posts(self):
        return Post.objects.filter(forum_categories=self).count()

    @property
    def last_post(self):
        return Post.objects.filter(forum_categories=self).latest("date")


class Reply(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content[:100]

    class Meta:
        verbose_name_plural = "replies"


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    replies = models.ManyToManyField(Reply, blank=True)

    def __str__(self):
        return self.content[:100]


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=400)
    slug = models.SlugField(max_length=400, unique=True, blank=True)
    content = HTMLField()
    forum_categories = models.ManyToManyField(Forum_Category)
    date = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=True)
    hit_count_generic = GenericRelation(HitCount, object_id_field='object_pk',related_query_name='hit_count_generic_relation')
    comments = models.ManyToManyField(Comment, blank=True)
    # closed = models.BooleanField(default=False)
    # state = models.CharField(max_length=40, default="zero")


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Post, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_url(self):
        return reverse("detail", kwargs= {
            "slug":self.slug
        })

    @property
    def num_comments(self):
        return self.comments.count()

    @property
    def last_reply(self):
        return self.comments.latest("date")




