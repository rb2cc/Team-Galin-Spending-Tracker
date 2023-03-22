from django.contrib import admin
from .models import User, Expenditure, Category, Challenge, UserChallenge, Level, UserLevel, Achievement, UserAchievement, Activity, Avatar
from .models import Author, Post, Forum_Category, Comment, Reply, Notification

admin.site.site_header = 'Admin Dashboard'
# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Configuration fo the admin interface for users."""
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'is_active')
    list_filter = ('is_staff',)
    fields = ('email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'is_active')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Configuration fo the admin interface for categories."""
    list_display = ('name', 'week_limit', 'is_global', 'is_overall', 'is_binned')
    fields = ('name', 'week_limit', 'is_global', 'is_overall', 'is_binned')

@admin.register(Expenditure)
class ExpenditureAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for expenditures"""

    list_display = ['id','user','title', 'expense','description', 'category','image','date_created', 'is_binned']

@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for challenges."""
    list_display = ['id', 'name', 'description', 'points', 'start_date', 'end_date']

@admin.register(UserChallenge)
class UserChallengeAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for user challenges."""
    list_display = ['id', 'user', 'challenge', 'date_entered', 'date_completed']

@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for levels."""
    list_display = ['name', 'description', 'required_points']

@admin.register(UserLevel)
class UserLevelAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for user levels."""
    list_display = ['user', 'level', 'points', 'date_reached']

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for achievements."""
    list_display = ['name', 'description', 'criteria', 'badge']

@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for user achievements."""
    list_display = ['user', 'achievement', 'date_earned']


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for activity."""
    list_display = ['user', 'image', 'name', 'time', 'points']

admin.site.register(Forum_Category)
admin.site.register(Author)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Reply)
admin.site.register(Avatar)
admin.site.register(Notification)
