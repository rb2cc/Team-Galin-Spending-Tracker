from django.test import TestCase, Client
from django.urls import reverse
from tracker.models import User


class MyActivityViewTests(TestCase):

    fixtures = ['tracker/tests/fixtures/default_user.json']

    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(email='galin@email.com')
        self.url = reverse('my_activity')

    def test_my_achievements_url(self):
        self.assertEqual(self.url, '/my_activity/')

    def test_my_achievements_view_uses_correct_template(self):
        self.client.login(email='galin@email.com', password='Password123')
        response = self.client.get(self.url, {'num_items': 'all'})
        self.assertTemplateUsed(response, 'my_activity.html')

    def test_correct_context(self):
        self.client.login(email='galin@email.com', password='Password123')
        response = self.client.get(self.url, {'num_items': 'all'})
        self.assertIn('user_activity', response.context)

    def test_without_num_items_equal_to_all(self):
        self.client.login(email='galin@email.com', password='Password123')
        response = self.client.get(self.url, {'num_items': '1'})
        self.assertEqual(response.status_code, 200)
