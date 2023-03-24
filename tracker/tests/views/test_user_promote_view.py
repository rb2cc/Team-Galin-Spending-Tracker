from django.test import TestCase, Client
from django.urls import reverse
from tracker.models import User

"""Unit tests for the user_promote view"""
class UserPromoteViewTest(TestCase):

    fixtures = ['tracker/tests/fixtures/default_user.json',
                'tracker/tests/fixtures/staff_users.json']

    def setUp(self):
        self.c = Client()
        self.superuser = User.objects.create_superuser(email='superuser@email.com', password='Password123')
        self.staff_user = User.objects.get(email='staff@email.com')
        self.url = reverse('user_promote')
        self.user = User.objects.get(email = 'galin@email.com')

    def test_user_promote_url(self):
        self.assertEqual(self.url, '/user_promote')

    def test_user_promote_success(self):
        self.c.login(email='superuser@email.com', password='Password123')
        response = self.c.post(self.url, {'user_pk': self.user.pk})
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_staff)
        self.assertRedirects(response, reverse('admin_dashboard'))

    def test_user_promote_user_does_not_exist(self):
        self.c.login(email='superuser@email.com', password='Password123')
        response = self.c.post(self.url, {'user_pk': 9999})
        self.assertRedirects(response, reverse('admin_dashboard'))

    def test_get_request(self):
        self.c.login(email='superuser@email.com', password='Password123')
        response = self.c.get(self.url)
        self.assertRedirects(response, reverse('admin_dashboard'))

    def test_no_primary_key(self):
        self.c.login(email='superuser@email.com', password='Password123')
        response = self.c.post(self.url, data= {})
        self.assertRedirects(response, reverse('admin_dashboard'))
