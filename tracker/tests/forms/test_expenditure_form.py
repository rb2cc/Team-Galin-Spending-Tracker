from django.core.exceptions import ValidationError
from django.test import TestCase
from django import forms
from tracker.forms import ExpenditureForm
from tracker.models import User,Category,Expenditure
from django.test.client import RequestFactory
import django.contrib.auth

"""Unit tests for the expenditure form"""

class RequestFormTestCase(TestCase):

    fixtures = ['tracker/tests/fixtures/default_user.json']

    def setUp(self): 

        self.factory = RequestFactory()
        url = 'test_image/fortlobby.png'
        
        self.user = User.objects.get(email = 'james@example.org')
        cat_three = Category.objects.create(name = 'Test3', week_limit = 200)
        self.user.available_categories.add(cat_three)

        category = Category.objects.create(
            name = 'Test',
            week_limit = 100,
            is_global = True
        )

        self.form_input={
            'title':'Test payment',
            'expense': 15,
            'description': 'Paying fellas',
            'category': cat_three,
            'image': url
        }
      
    def test_valid_expenditure_form(self):
        request=self.factory.get('landing_page/')
        request.user = self.user
        
        form = ExpenditureForm(data=self.form_input, r=request)
        print(form.errors)
        self.assertTrue(form.is_valid())

    def test_form_has_all_fields(self):
        request=self.factory.get('landing_page/')
        request.user = self.user
        form = ExpenditureForm(r=request)
        self.assertIn('title', form.fields)
        self.assertIn('expense', form.fields)
        self.assertIn('description', form.fields)
        self.assertIn('category', form.fields)
        self.assertIn('image', form.fields)
        
    def test_form_must_save_correctly(self):
        pass