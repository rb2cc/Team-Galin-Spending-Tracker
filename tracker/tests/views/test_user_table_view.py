from django.test import TestCase, Client
from django.urls import reverse
from tracker.models import User

"""Unit tests for the user_table view"""
class UserTableViewTest(TestCase):

    fixtures = ['tracker/tests/fixtures/default_user.json',
                'tracker/tests/fixtures/staff_users.json']

    def setUp(self):
        self.c = Client()
        self.superuser = User.objects.create_superuser(email='superuser@email.com', password='Password123')
        self.staff_user = User.objects.get(email='staff@email.com')
        self.url = reverse('user_table')

    def test_user_table_url(self):
        self.assertEqual(self.url, '/user_table/')

    def test_get_user_table(self):
        self.c.login(email='superuser@email.com', password='Password123')
        response = self.c.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_table.html')

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
