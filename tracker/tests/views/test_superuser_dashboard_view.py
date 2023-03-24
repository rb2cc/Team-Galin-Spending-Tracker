from django.test import TestCase, Client
from django.urls import reverse
from tracker.models import User, Category, Challenge, Achievement
from django.core.paginator import Paginator
import datetime

"""Unit tests for the admin_dashboard view"""
class AdminDashboardViewTestCase(TestCase):

    fixtures = ['tracker/tests/fixtures/default_user.json']

    def setUp(self):
        self.c = Client()
        self.superuser = User.objects.create_superuser(email='superuser@email.com', password='Password123')
        self.staff_user = User.objects.create_user(email='staff@email.com', password='Password123', is_staff=True)
        self.non_staff_user = User.objects.get(email='galin@email.com')
        self.url = reverse('superuser_dashboard')

    def test_superuser_dashboard_url(self):
        self.assertEqual(self.url, '/superuser_dashboard/')

    def test_view_uses_correct_template(self):
        self.client.login(email='superuser@email.com', password='Password123')
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'superuser_dashboard.html')

    def test_correct_context(self):
        self.client.login(email='superuser@email.com', password='Password123')
        response = self.client.get(self.url)
        self.assertIn('form', response.context)
        self.assertIn('page', response.context)

    def test_post_request(self):
        self.client.login(email='superuser@email.com', password='Password123')
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@email.com',
            'new_password': 'Pass123',
            'password_confirmation': 'Pass123'
        }

        response = self.client.post(self.url, data)
        self.assertTrue(User.objects.filter(email='test@email.com').exists())

    def test_post_request_with_will_be_admin(self):
        self.client.login(email='superuser@email.com', password='Password123')
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@email.com',
            'new_password': 'Pass123',
            'password_confirmation': 'Pass123',
            'will_be_admin': '1'
        }
        response = self.client.post(self.url, data)
        self.assertTrue(User.objects.filter(email='test@email.com').exists())
        self.assertTrue(User.objects.get(email='test@email.com').is_staff)

    def test_post_invalid_form_superuser_dashboard(self):
        self.client.login(email='superuser@email.com', password='Password123')
        response = self.client.post(self.url, {'email': 'test@email.com'})
        self.assertTrue(response.status_code, 200)
