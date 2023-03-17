from django.test import TestCase, Client
from django.urls import reverse
from tracker.models import User

"""Unit tests for the user_table view"""
class UserTableViewTest(TestCase):

    fixtures = ['tracker/tests/fixtures/default_user.json']

    def setUp(self):
        self.c = Client()
        superuser = User.objects.create_superuser(email='superuser@email.com', password='Password123')
        self.c.login(email='superuser@email.com', password='Password123')
        self.url = reverse('user_table')
        self.user = User.objects.get(email = 'galin@email.com')

    def test_user_table_url(self):
        self.assertEqual(self.url, '/user_table/')

    def test_get_user_table(self):
        response = self.c.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_table.html')
        
