from django.test import TestCase, Client
from django.urls import reverse
from tracker.models import User, Challenge

"""Unit tests for the challenge_table view"""
class UserTableViewTest(TestCase):

    fixtures = ['tracker/tests/fixtures/default_user.json']

    def setUp(self):
        self.c = Client()
        superuser = User.objects.create_superuser(email='superuser@email.com', password='Password123')
        self.url = reverse('challenge_table')
        self.user = User.objects.get(email = 'galin@email.com')

    def test_challenge_table_url(self):
        self.assertEqual(self.url, '/challenge_table/')

    def test_get_challenge_table(self):
        self.c.login(email='superuser@email.com', password='Password123')
        response = self.c.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'challenge_table.html')

    def test_correct_number_of_challenges(self):
        self.c.login(email='superuser@email.com', password='Password123')
        response = self.c.get(self.url)
        number_of_challenges = Challenge.objects.count()
        paginator_number_of_challenges = response.context['challenge_page'].paginator.count
        self.assertEqual(number_of_challenges, paginator_number_of_challenges)
