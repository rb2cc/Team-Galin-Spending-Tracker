from django.test import TestCase, Client
from django.urls import reverse
from tracker.models import User, Category, Challenge, Achievement
import datetime

"""Unit tests for the delete view"""
class DeleteViewTestCase(TestCase):

    fixtures = ['tracker/tests/fixtures/default_user.json']

    def setUp(self):
        self.c = Client()
        superuser = User.objects.create_superuser(email='superuser@email.com', password='Password123')
        self.c.login(email='superuser@email.com', password='Password123')
        self.url = reverse('delete')
        self.user = User.objects.get(email = 'galin@email.com')
        self.category = Category.objects.create(name = 'Category', week_limit = 10)
        self.challenge = Challenge.objects.create(name = 'Challenge', description = '', points = 10, start_date = datetime.date(2023, 3, 3), end_date = datetime.date(2023, 3, 4))
        self.achievement = Achievement.objects.create(name = 'Achievement', description='', criteria='')

    def test_delete_url(self):
        self.assertEqual(self.url, '/delete')

    def test_delete_view_deletes_user(self):
        before_count = User.objects.count()
        response = self.c.post(self.url, {'user_pk': self.user.pk})
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count-1)
        self.assertRedirects(response, reverse('admin_dashboard'))

    def test_delete_user_does_not_exist(self):
        before_count = User.objects.count()
        response = self.c.post(self.url, {'user_pk': 9999})
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertRedirects(response, reverse('admin_dashboard'))

    def test_delete_view_deletes_category(self):
        before_count = Category.objects.count()
        response = self.c.post(self.url, {'category_pk': self.category.pk})
        after_count = Category.objects.count()
        self.assertEqual(after_count, before_count-1)
        self.assertRedirects(response, reverse('admin_dashboard'))

    def test_delete_category_does_not_exist(self):
        before_count = Category.objects.count()
        response = self.c.post(self.url, {'category_pk': 9999})
        after_count = Category.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertRedirects(response, reverse('admin_dashboard'))

    def test_delete_view_deletes_challenge(self):
        before_count = Challenge.objects.count()
        response = self.c.post(self.url, {'challenge_pk': self.challenge.pk})
        after_count = Challenge.objects.count()
        self.assertEqual(after_count, before_count-1)
        self.assertRedirects(response, reverse('admin_dashboard'))

    def test_delete_challenge_does_not_exist(self):
        before_count = Challenge.objects.count()
        response = self.c.post(self.url, {'challenge_pk': 9999})
        after_count = Challenge.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertRedirects(response, reverse('admin_dashboard'))

    def test_delete_view_deletes_achievement(self):
        before_count = Achievement.objects.count()
        response = self.c.post(self.url, {'achievement_pk': self.achievement.pk})
        after_count = Achievement.objects.count()
        self.assertEqual(after_count, before_count-1)
        self.assertRedirects(response, reverse('admin_dashboard'))

    def test_delete_achievement_does_not_exist(self):
        before_count = Achievement.objects.count()
        response = self.c.post(self.url, {'achievement_pk': 9999})
        after_count = Achievement.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertRedirects(response, reverse('admin_dashboard'))
