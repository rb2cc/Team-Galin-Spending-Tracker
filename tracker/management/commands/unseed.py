from django.core.management.base import BaseCommand, CommandError
from tracker.models import UserManager, User, Expenditure, Notification, Post, Reply, Achievement, Activity, Avatar, Category, Challenge, Forum_Category, Level, UserLevel



class Command(BaseCommand):
    
    def handle(self, *args, **options):

        User.objects.all().delete()
        Expenditure.objects.all().delete()
        Notification.objects.all().delete()
        Post.objects.all().delete()
        Reply.objects.all().delete()
        Achievement.objects.all().delete()
        Activity.objects.all().delete()
        Avatar.objects.all().delete()
        Category.objects.all().delete()
        Challenge.objects.all().delete()
        Forum_Category.objects.all().delete()
        Level.objects.all().delete()
        UserLevel.objects.all().delete()
