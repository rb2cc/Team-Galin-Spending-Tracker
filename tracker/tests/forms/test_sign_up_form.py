from django.contrib.auth.hashers import check_password
from django import forms
from django.test import TestCase
from tracker.forms import SignUpForm
from tracker.models import User

class SignUpFormTestCase(TestCase):
    '''Unit tests of the sign up form'''

    def setUp(self):
        self.form_input = {
            'first_name' : 'James',
            'last_name' : 'Lu',
            'email' : 'james@example.org',
            'new_password' : 'Lu123',
            'password_confirmation' : 'Lu123'
        }

    def test_valid_sign_up_form(self):
        form = SignUpForm(data = self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = SignUpForm()
        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)
        self.assertIn('new_password', form.fields)
        self.assertIn('email', form.fields)
        new_password_widget = form.fields['new_password'].widget
        self.assertTrue(isinstance(new_password_widget, forms.PasswordInput))
        self.assertIn('password_confirmation', form.fields)
        password_confirmation_widget = form.fields['password_confirmation'].widget
        self.assertTrue(isinstance(password_confirmation_widget, forms.PasswordInput))

    def test_form_user_model_validation(self):
        self.form_input['email'] = 'bademail'
        form = SignUpForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_uppercase_character(self):
        self.form_input['new_password'] = 'lu123'
        self.form_input['password_confirmation'] = 'lu123'
        form = SignUpForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_lowercase_character(self):
        self.form_input['new_password'] = 'LU123'
        self.form_input['password_confirmation'] = 'LU1123'
        form = SignUpForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_number_character(self):
        self.form_input['new_password'] = 'Lu'
        self.form_input['password_confirmation'] = 'Lu'
        form = SignUpForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_identical(self):
        self.form_input['password_confirmation'] = 'WrongPassword123'
        form = SignUpForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        form = SignUpForm(data = self.form_input)
        before_count = User.objects.count()
        form.save()
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count+1)
        user = User.objects.get(email = 'james@example.org')
        self.assertEqual(user.first_name,'James')
        self.assertEqual(user.last_name,'Lu')
        is_password_correct = check_password('Lu123', user.password)
        self.assertTrue(is_password_correct)
