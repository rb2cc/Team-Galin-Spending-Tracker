from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin, User
from personal_spending_tracker import settings

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

    objects = UserManager()
    USERNAME_FIELD = 'email'

class Expenditure(models.Model):
    """Expenditure model for user spending"""

    title = models.CharField(max_length=25, blank=False)
    description = models.TextField(max_length=280, blank=False)
    image = models.ImageField(editable=True, blank=True, upload_to='images')
    expense = models.DecimalField(max_digits=20,decimal_places=2, null=False)
    date_created = models.DateField(auto_now=True)
    # category = models.ForeignKey(Category, on_delete=models.CASCADE) #uncomment when category model is implemented

