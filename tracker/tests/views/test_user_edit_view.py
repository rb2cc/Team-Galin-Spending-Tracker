from django.urls import reverse
from tracker.forms import EditUserForm
from tracker.models import User, Activity
from django.test import TestCase

class UserEditViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpassword',
            first_name='Test',
            last_name='User'
        )
        self.url = reverse('edit_user')
        self.client.login(email='testuser@example.com', password='testpassword')

    def test_initial_form_values(self):
        response = self.client.get(self.url)
        form = response.context['form']
        self.assertEqual(form.initial['email'], 'testuser@example.com')
        self.assertEqual(form.initial['first_name'], 'Test')
        self.assertEqual(form.initial['last_name'], 'User')

    def test_update_one_field(self):
        data = {
            'email': 'updateduser@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'username':'test',
        }
        response = self.client.post(self.url, data)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'updateduser@example.com')
        self.assertEqual(self.user.first_name, 'Test')
        self.assertEqual(self.user.last_name, 'User')
        self.assertRedirects(response, reverse('landing_page'))
        activity_name = f'You\'ve changed your email from testuser@example.com to updateduser@example.com'
        self.assertEqual(Activity.objects.filter(user=self.user, name=activity_name).count(), 1)

    def test_update_multiple_fields(self):
        data = {
            'email': 'updateduser@example.com',
            'first_name': 'Updated',
            'last_name': 'Usernew',
            'username':'test',
        }
        response = self.client.post(self.url, data)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'updateduser@example.com')
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.last_name, 'Usernew')
        self.assertRedirects(response, reverse('landing_page'))
        activity_name1 = f'You\'ve changed your email from testuser@example.com to updateduser@example.com'
        activity_name2 = f'You\'ve changed your first name from Test to Updated'
        self.assertEqual(Activity.objects.filter(user=self.user, name=activity_name1).count(), 1)
        self.assertEqual(Activity.objects.filter(user=self.user, name=activity_name2).count(), 1)

    def test_update_zero_fields(self):
        data = {
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'username': self.user.username,
        }
        before_count = Activity.objects.filter(user=self.user).count()
        response = self.client.post(self.url, data)
        after_count = Activity.objects.filter(user=self.user).count()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(before_count, after_count)

