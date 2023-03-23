from django.core.management.base import BaseCommand, CommandError
from tracker.models import UserManager, User, Expenditure, Notification, Post, Reply



class Command(BaseCommand):
    def handle(self, *args, **options):

        User.objects.filter(is_superuser=False).delete()
        Expenditure.objects.all().delete()
        Notification.objects.all().delete()
        Post.objects.all().delete()
        Reply.objects.all().delete()
