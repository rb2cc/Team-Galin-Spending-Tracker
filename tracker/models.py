from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin, User
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from personal_spending_tracker import settings
from decimal import Decimal
from django.utils import timezone

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

    objects = UserManager()
    USERNAME_FIELD = 'email'



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

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

class Expenditure(models.Model):
    """Expenditure model for user spending"""

    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1) #uncomment when category model is implemented
    title = models.CharField(max_length=20, blank=False)
    description = models.TextField(max_length=280, blank=False)
    image = models.ImageField(editable=True, upload_to='images', blank=True)
    expense = models.DecimalField(max_digits=20, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], null=False)
    date_created = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

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

