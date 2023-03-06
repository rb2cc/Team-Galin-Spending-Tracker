from django.core.exceptions import ValidationError
from django.test import TestCase
from tracker.models import User, Category

"""Unit tests for the category model"""
class CategoryModelTestCase(TestCase):

    fixtures = ['tracker/tests/fixtures/default_user.json',
                'tracker/tests/fixtures/default_category.json']
    
    def setUp(self):
        
        self.user = User.objects.get(email = 'james@example.org')

        self.category = Category.objects.get(name = 'Test')

    def test_valid_category(self):
        self._assert_category_is_valid()

    def test_category_name_cannot_be_blank(self):
        self.category.name = ''
        self._assert_category_is_invalid()

    def test_category_name_can_be_50_long(self):
        self.category.name = 'x' * 50
        self._assert_category_is_valid()

    def test_category_name_cannot_be_51_long(self):
        self.category.name = 'x' * 51
        self._assert_category_is_invalid()

    def test_category_week_limit_cannot_be_blank(self):
        self.category.week_limit = None
        self._assert_category_is_invalid()

    def test_category_week_limit_cannot_be_negative(self):
        self.category.week_limit = -4
        self._assert_category_is_invalid

    def _assert_category_is_valid(self):
        try:
            self.category.full_clean()
        except (ValidationError):
            self.fail('Test category should be valid')

    def _assert_category_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.category.full_clean()

