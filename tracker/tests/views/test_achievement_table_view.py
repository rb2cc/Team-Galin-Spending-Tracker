from django.test import TestCase, Client
from django.urls import reverse
from tracker.models import User, Achievement

"""Unit tests for the achievement_table view"""
class UserTableViewTest(TestCase):

    fixtures = ['tracker/tests/fixtures/default_user.json']

    def setUp(self):
        self.c = Client()
        superuser = User.objects.create_superuser(email='superuser@email.com', password='Password123')
        self.url = reverse('achievement_table')
        self.user = User.objects.get(email = 'galin@email.com')

    def test_achievement_table_url(self):
        self.assertEqual(self.url, '/achievement_table/')

    def test_get_achievement_table(self):
        self.c.login(email='superuser@email.com', password='Password123')
        response = self.c.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'achievement_table.html')

    def test_correct_number_of_achievements(self):
        self.c.login(email='superuser@email.com', password='Password123')
        response = self.c.get(self.url)
        number_of_achievements = Achievement.objects.count()
        paginator_number_of_achievements = response.context['achievement_page'].paginator.count
        self.assertEqual(number_of_achievements, paginator_number_of_achievements)
