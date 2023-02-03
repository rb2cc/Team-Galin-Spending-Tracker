from django.contrib import admin
from .models import User, Expenditure, Category


# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Configuration fo the admin interface for users."""
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'is_active')
    fields = ('email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'is_active')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Configuration fo the admin interface for categories."""
    list_display = ('name', 'week_limit', 'is_global')
    fields = ('name', 'week_limit', 'is_global')

@admin.register(Expenditure)
class UserAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for expenditures"""
    list_display = ['id','title', 'expense','description', 'image','date_created']

