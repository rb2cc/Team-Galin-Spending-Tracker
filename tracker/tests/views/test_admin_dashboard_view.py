from django.test import TestCase, Client
from django.urls import reverse
from tracker.models import User, Category, Challenge, Achievement
import datetime

"""Unit tests for the admin_dashboard view"""
class DeleteViewTestCase(TestCase):

    fixtures = ['tracker/tests/fixtures/default_user.json']

    def setUp(self):
        self.c = Client()
        superuser = User.objects.create_superuser(email='superuser@email.com', password='Password123')
        self.c.login(email='superuser@email.com', password='Password123')
        self.url = reverse('admin_dashboard')
        self.user = User.objects.get(email = 'galin@email.com')
        self.category = Category.objects.create(name = 'Category', week_limit = 10)
        self.challenge = Challenge.objects.create(name = 'Challenge', description = '', points = 10, start_date = datetime.date(2023, 3, 3), end_date = datetime.date(2023, 3, 4))
        self.achievement = Achievement.objects.create(name = 'Achievement', description='', criteria='')

    def test_delete_url(self):
        self.assertEqual(self.url, '/admin_dashboard/')
