from django.test import TestCase, Client
from django.urls import reverse
from tracker.models import User


class MyAchievementsViewTests(TestCase):

    fixtures = ['tracker/tests/fixtures/default_user.json']

    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(email='galin@email.com')
        self.url = reverse('my_achievements')

    def test_my_achievements_url(self):
        self.assertEqual(self.url, '/my_achievements/')

    def test_my_achievements_view_uses_correct_template(self):
        self.client.login(email='galin@email.com', password='Password123')
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'my_achievements.html')

    def test_correct_context(self):
        self.client.login(email='galin@email.com', password='Password123')
        response = self.client.get(self.url)
        self.assertIn('user_achievements', response.context)
