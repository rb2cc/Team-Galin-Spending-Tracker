from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.urls import reverse
from tracker.forms import SignUpForm
from tracker.models import User, Category
from .helpers import LogInTester, CategoryFunctions


class SignUpViewTestCase(TestCase, LogInTester):

    def setUp(self):
        self.url = reverse('sign_up')
        self.form_input = {
            'first_name' : 'James',
            'last_name' : 'Lu',
            'email' : 'james@example.org',
            'new_password' : 'Lu123',
            'password_confirmation' : 'Lu123'
        }
        CategoryFunctions._make_categories(self)

    def test_sign_up_url(self):
        self.assertEqual(self.url, '/sign_up/')

    def test_get_sign_up(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sign_up.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, SignUpForm))
        self.assertFalse(form.is_bound)

    def test_unsuccessful_sign_up(self):
        self.form_input['email'] = 'bademail'
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sign_up.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, SignUpForm))
        self.assertTrue(form.is_bound)
        self.assertFalse(self._is_logged_in())

    def test_successful_sign_up(self):
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count+1)
        response_url = reverse('landing_page')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing_page.html')
        user = User.objects.get(email = 'james@example.org')
        self.assertEqual(user.first_name,'James')
        self.assertEqual(user.last_name,'Lu')
        is_password_correct = check_password('Lu123', user.password)
        self.assertTrue(is_password_correct)
        self.assertTrue(self._is_logged_in())

    def test_global_categories_assigned_on_signup(self):
        self.client.post(self.url, self.form_input, follow=True)
        user = User.objects.get(email = 'james@example.org')
        self.assertEqual(Category.objects.all().count(), 5)
        self.assertEqual(user.available_categories.all().count(), 2)


