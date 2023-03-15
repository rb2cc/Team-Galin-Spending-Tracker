from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.urls import reverse
from tracker.forms import SignUpForm
from tracker.models import User, Category, Achievement
from tracker.tests.helpers import LogInTester, CategoryFunctions
from django.core.exceptions import ObjectDoesNotExist

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
        self.achievement = Achievement.objects.create(name = "New user", description = "Test", criteria = "Test", badge = "Test")

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

    def test_correct_categories_assigned_on_signup(self):
        self.client.post(self.url, self.form_input, follow=True)
        user = User.objects.get(email = 'james@example.org')
        self.assertEqual(Category.objects.all().count(), 6)
        self.assertEqual(user.available_categories.all().count(), 3)
        self.assertEqual(user.available_categories.filter(is_overall = True).count(), 1)

    def test_sign_up_with_existing_email(self):
        User.objects.create_user(
            email='james@example.org',
            password='Lu123',
            first_name='James',
            last_name='Lu'
        )
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
        self.assertTrue('This email has already been registered' in response.content.decode())

    def test_sign_up_without_new_user_achievement(self):
        self.achievement.delete()
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count+1)
        response_url = reverse('landing_page')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing_page.html')
        user = User.objects.get(email='james@example.org')
        with self.assertRaises(ObjectDoesNotExist):
            user.userachievement_set.get(achievement__name="New user")

