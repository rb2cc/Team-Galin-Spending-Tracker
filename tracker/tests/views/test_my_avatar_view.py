from django.test import TestCase, Client
from django.urls import reverse
from tracker.models import User, Level, UserLevel, Activity


class MyAchievementsViewTests(TestCase):

    fixtures = ['tracker/tests/fixtures/default_user.json']

    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(email='galin@email.com')
        self.level = Level.objects.create(name='level', description='description', required_points=10)
        self.userlevel = UserLevel.objects.create(user=self.user, level=self.level, points=10000)

        self.url = reverse('my_avatar')

    def test_view_requires_authentication(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_view_uses_correct_template(self):
        self.userlevel.delete()
        UserLevel.objects.create(user=self.user, level=self.level, points=0)
        self.client.login(email='galin@email.com', password='Password123')
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'my_avatar.html')

    def test_correct_context(self):
        self.client.login(email='galin@email.com', password='Password123')
        response = self.client.get(self.url)
        self.assertIn('components', response.context)
        self.assertIn('colours', response.context)
        self.assertIn('locked_items', response.context)
        self.assertIn('tier_info', response.context)
        self.assertIn('user_tier_colour', response.context)
        self.assertEqual(response.status_code, 200)

    def test_with_random(self):
        self.client.login(email='galin@email.com', password='Password123')
        response = self.client.get(self.url, {'random': ''})
        self.assertEqual(response.status_code, 200)

    def test_with_clear(self):
        self.client.login(email='galin@email.com', password='Password123')
        response = self.client.get(self.url, {'clear': ''})
        self.assertEqual(response.status_code, 200)

    def test_already_edited_before(self):
        Activity.objects.create(user=self.user, name="You've created an avatar")
        self.client.login(email='galin@email.com', password='Password123')
        response = self.client.get(self.url, {'random': ''})
        self.assertEqual(response.status_code, 200)
