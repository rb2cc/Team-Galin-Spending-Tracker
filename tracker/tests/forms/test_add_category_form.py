from django import forms
from django.test import TestCase
from tracker.forms import AddCategoryForm
from tracker.models import Category

"""Unit tests for the AddCategory form"""
class AddCategoryFormTestCase(TestCase):

    def setUp(self):

        self.category = Category.objects.create(
            name = 'Test',
            week_limit = 100,
        )

        self.form_input = {
            'name':'New',
            'week_limit':30
        }

    def test_valid_add_category_form(self):
        form = AddCategoryForm(data = self.form_input)
        self.assertTrue(form.is_valid())

    def test_add_category_form_has_necessary_fields(self):
        form = AddCategoryForm()
        self.assertIn('name', form.fields)
        self.assertIn('week_limit', form.fields)

    def test_invalid_add_category_form(self):
        self.form_input['name'] = 'x' * 51
        form = AddCategoryForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_add_category_form_saves_correctly(self):
        form = AddCategoryForm(data = self.form_input)
        before_count = Category.objects.count()
        form.save()
        after_count = Category.objects.count()
        self.assertEqual(after_count, before_count+1)
        added_category = Category.objects.get(name = 'New')
        self.assertEqual(added_category.week_limit, 30)
        self.assertEqual(added_category.is_global, False)
        
    