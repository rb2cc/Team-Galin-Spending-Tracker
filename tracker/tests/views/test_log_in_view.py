from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from tracker.forms import LogInForm
from tracker.models import User
from tracker.tests.helpers import LogInTester

class LogInViewTestCase(TestCase, LogInTester):

    fixtures = ['tracker/tests/fixtures/default_user.json']

    def setUp(self):
        self.url = reverse('home')
        self.user = User.objects.get(email = 'james@example.org')

    def test_log_in_url(self):
        self.assertEqual(self.url, '/')

    def test_get_log_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list),0)

    def test_unsuccessful_log_in(self):
        form_input = {'email':'james@example.org', 'password':'WrongPassword123'}
        response = self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(self._is_logged_in())
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list),1)
        self.assertEqual(messages_list[0].level,messages.ERROR)

    def test_successful_log_in(self):
        form_input = {'email':'james@example.org', 'password':'Lu123'}
        response = self.client.post(self.url, form_input, follow=True)
        self.assertTrue(self._is_logged_in())
        response_url = reverse('landing_page')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing_page.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list),0)

    def test_valid_log_in_by_inactive_user(self):
        self.user.is_active = False
        self.user.save()
        form_input = {'email':'james@example.org', 'password':'Lu123'}
        response = self.client.post(self.url, form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(self._is_logged_in())
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list),1)
        self.assertEqual(messages_list[0].level,messages.ERROR)

    def test_log_out(self):
        self.client.login(username='james@example.org', password='Lu123')
        self.assertTrue(self._is_logged_in())
        log_out_url = reverse('log_out')
        response = self.client.get(log_out_url, follow=True)
        self.assertFalse(self._is_logged_in())
        self.assertRedirects(response, self.url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')

