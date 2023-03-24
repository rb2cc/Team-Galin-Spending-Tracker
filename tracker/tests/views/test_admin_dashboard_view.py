from django.test import TestCase, Client
from django.urls import reverse
from tracker.models import User, Category, Challenge, Achievement
from django.core.paginator import Paginator
import datetime

"""Unit tests for the admin_dashboard view"""
class AdminDashboardViewTestCase(TestCase):

    fixtures = ['tracker/tests/fixtures/default_user.json',
                'tracker/tests/fixtures/staff_users.json']

    def setUp(self):
        self.c = Client()
        self.superuser = User.objects.create_superuser(email='superuser@email.com', password='Password123')
        self.staff_user = User.objects.get(email='staff@email.com')
        self.non_staff_user = User.objects.get(email='non-staff@email.com')
        self.url = reverse('admin_dashboard')

    def test_admin_dashboard_url(self):
        self.assertEqual(self.url, '/admin_dashboard/')

    def test_non_staff_trying_to_access_page(self):
        login = self.c.login(email='non-staff@email.com', password='Password123')
        response = self.c.get(self.url)
        self.assertRedirects(response, reverse('landing_page'))

    def test_staff_trying_to_access_page(self):
        self.c.login(email='staff@email.com', password='Password123')
        response = self.c.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_dashboard.html')
        self.assertIn('view', response.context)
        self.assertIn('user_page', response.context)
        self.assertIn('category_page', response.context)
        self.assertIn('challenge_page', response.context)
        self.assertIn('achievement_page', response.context)
        self.assertIn('user_form', response.context)
        self.assertIn('category_form', response.context)
        self.assertIn('challenge_form', response.context)
        self.assertIn('achievement_form', response.context)

    def test_creating_user(self):
        self.c.login(email='staff@email.com', password='Password123')
        response = self.c.post(self.url, data = {
            'create_user': '',
            'email': 'galinski@email.com',
            'first_name': 'galin',
            'last_name': 'mihaylov',
            'new_password': 'Password123',
            'password_confirmation': 'Password123'
        })
        self.assertTrue(User.objects.filter(email='galinski@email.com').exists())
        self.assertRedirects(response, self.url)

    def test_creating_bad_user(self):
        self.c.login(email='staff@email.com', password='Password123')
        response = self.c.post(self.url, data = {
            'create_user': '',
            'email': 'galinski@email.com',
            'first_name': 'galin',
            'last_name': 'mihaylov',
            'new_password': 'Password123',
            'password_confirmation': 'Password1'
        }, follow=True)
        self.assertFalse(User.objects.filter(email='galinski@email.com').exists())
        self.assertRedirects(response, self.url)

    def test_creating_category(self):
        self.c.login(email='staff@email.com', password='Password123')
        response = self.c.post(self.url, data = {
            'create_category': '',
            'name': 'Category',
            'week_limit': '10',
        })
        self.assertTrue(Category.objects.filter(name='Category').exists())
        self.assertRedirects(response, self.url)

    def test_creating_bad_category(self):
        self.c.login(email='staff@email.com', password='Password123')
        response = self.c.post(self.url, data = {
            'create_category': '',
            'name': 'Category',
            'week_limit': 'abc',
        })
        self.assertFalse(Category.objects.filter(name='Category').exists())
        self.assertRedirects(response, self.url)

    def test_creating_challenge(self):
        self.c.login(email='staff@email.com', password='Password123')
        response = self.c.post(self.url, data = {
            'create_challenge': '',
            'name': 'Challenge',
            'description': 'Description',
            'points': '10',
            'start_date': datetime.date(2023, 3, 3),
            'end_date': datetime.date(2023, 3, 4),
        })
        self.assertTrue(Challenge.objects.filter(name='Challenge').exists())
        self.assertRedirects(response, self.url)

    def test_creating_bad_challenge(self):
        self.c.login(email='staff@email.com', password='Password123')
        response = self.c.post(self.url, data = {
            'create_challenge': '',
            'name': 'Challenge',
            'description': 'Description',
            'points': 'abc',
            'start_date': datetime.date(2023, 3, 3),
            'end_date': datetime.date(2023, 3, 4),
        })
        self.assertFalse(Challenge.objects.filter(name='Challenge').exists())
        self.assertRedirects(response, self.url)

    def test_creating_achievement(self):
        self.c.login(email='staff@email.com', password='Password123')
        response = self.c.post(self.url, data = {
            'create_achievement': '',
            'name': 'Achievement',
            'description': 'Description',
            'criteria': 'Criteria'
        })
        self.assertTrue(Achievement.objects.filter(name='Achievement').exists())
        self.assertRedirects(response, self.url)

    def test_creating_bad_achievement(self):
        self.c.login(email='staff@email.com', password='Password123')
        response = self.c.post(self.url, data = {
            'create_achievement': '',
            'name': 'Achievement',
            'description': '',
            'criteria': ''
        })
        self.assertFalse(Achievement.objects.filter(name='Achievement').exists())
        self.assertRedirects(response, self.url)

    def test_superuser_creating_user_as_staff(self):
        self.c.login(email='superuser@email.com', password='Password123')
        response = self.c.post(self.url, data = {
            'create_user': '',
            'will_be_admin': '1',
            'email': 'galinski@email.com',
            'first_name': 'galin',
            'last_name': 'mihaylov',
            'new_password': 'Password123',
            'password_confirmation': 'Password123'
        })
        self.assertTrue(User.objects.filter(email='galinski@email.com').exists())
        self.assertTrue(User.objects.get(email='galinski@email.com').is_staff)
        self.assertRedirects(response, self.url)

    def test_user_list_for_superuser(self):
        self.c.login(email='superuser@email.com', password='Password123')
        response = self.c.get(self.url)
        number_of_users = User.objects.count()
        paginator_number_of_users = response.context['user_page'].paginator.count
        self.assertEqual(number_of_users, paginator_number_of_users)

    def test_user_list_for_staff(self):
        self.c.login(email='staff@email.com', password='Password123')
        response = self.c.get(self.url)
        non_staff_number_of_users = User.objects.filter(is_staff=False).count()
        paginator_number_of_users = response.context['user_page'].paginator.count
        self.assertEqual(non_staff_number_of_users, paginator_number_of_users)
