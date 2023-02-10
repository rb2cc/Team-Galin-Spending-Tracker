from django.core.exceptions import ValidationError
from django.test import TestCase
from django import forms
from tracker.forms import ExpenditureForm
from tracker.models import User,Category,Expenditure

"""Unit tests for the expenditure form"""

class RequestFormTestCase(TestCase):
    def setUp(self): 

        url = 'images/fortlobby.png'

        self.category = Category.objects.create(
            name = 'Test',
            week_limit = 100,
        )

        self.form_input={
            'title':'Test payment',
            'expense': 15,
            'description': 'Paying fellas',
            'category': self.category,
            'image': url
        }
                
    def test_valid_expenditure_form(self):
        form = ExpenditureForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_all_fields(self):
        form = ExpenditureForm()
        self.assertIn('title', form.fields)
        self.assertIn('expense', form.fields)
        self.assertIn('description', form.fields)
        self.assertIn('category', form.fields)
        self.assertIn('image', form.fields)