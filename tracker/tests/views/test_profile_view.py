from django.test import TestCase, Client
from django.urls import reverse
from tracker.models import User, UserLevel, Level
from tracker.tests.helpers import delete_avatar_after_test


class ProfileViewTests(TestCase):

    fixtures = ['tracker/tests/fixtures/default_user.json']

    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(email='galin@email.com')
        self.level = Level.objects.create(name='level', description='description', required_points=10)
        self.userlevel = UserLevel.objects.create(user=self.user, level=self.level, points=20)
        self.url = reverse('profile', kwargs={'id': self.user.id})

    def test_view_url(self):
        self.assertEqual(self.url, f'/profile/{self.user.id}')

    def test_view_uses_correct_template(self):
        self.client.login(email='galin@email.com', password='Password123')
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'profile.html')

    def test_correct_context(self):
        self.client.login(email='galin@email.com', password='Password123')
        response = self.client.get(self.url)
        self.assertIn('profile_user', response.context)
        self.assertIn('user_tier_colour', response.context)
        self.assertIn('user_tier_name', response.context)
        self.assertIn('current_level_name', response.context)
        self.assertIn('user_level', response.context)
        self.assertIn('avatar', response.context)
        self.assertIn('user_achievements', response.context)
        self.assertIn('user_posts', response.context)

    def test_with_reached_tiers(self):
        self.client.login(email='galin@email.com', password='Password123')
        self.userlevel.delete()
        UserLevel.objects.create(user=self.user, level=self.level, points=10000)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_profile_with_existing_avatar_template(self):
        self.client.login(email='galin@email.com', password='Password123')
        url = reverse('my_avatar')
        response = self.client.get(url, {'random': ''})
        self.assertEqual(response.status_code, 200)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        delete_avatar_after_test(self)

    def test_profile_with_deleted_avatar_template(self):
        self.client.login(email='galin@email.com', password='Password123')
        url = reverse('my_avatar')
        response = self.client.get(url, {'random': ''})
        self.assertEqual(response.status_code, 200)
        delete_avatar_after_test(self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)