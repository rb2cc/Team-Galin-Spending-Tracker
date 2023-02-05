from django.core.exceptions import ValidationError
from django.test import TestCase
from tracker.models import User, Category, Expenditure


"""Unit tests for the expenditure model"""
class ExpenditureModelTestCase(TestCase):

    def setUp(self):

        url = 'images/fortlobby.png'

        self.user = User.objects.create_user(
            email = 'james@example.org',
            first_name='James',
            last_name = 'Lu',
            password = 'Lu123',
        )

        self.category = Category.objects.create(
            name = 'Test',
            week_limit = 100,
        )
        
        self.expenditure = Expenditure.objects.create(
            category = self.category,
            title = 'Test payment',
            description = 'Paying fellas',
            expense = 15,
            image = url,
            user = self.user
        )

    def test_valid_expenditure(self):
        self._assert_expenditure_is_valid()

    def test_expenditure_category_cannot_be_blank(self):
        self.expenditure.category=None
        self._assert_expenditure_is_invalid()

    def test_expenditure_user_cannot_be_blank(self):
        self.expenditure.user=None
        self._assert_expenditure_is_invalid

    def test_expense_cannot_be_more_than_20_digits(self):
        self.expenditure.expense=1000000000000000000.00
        self._assert_expenditure_is_invalid

    def test_expense_cannot_have_more_than_2_decimal_places(self):
        self.expenditure.expense=100.555
        self._assert_expenditure_is_invalid

    def test_expense_cannot_be_blank(self):
        self.expenditure.expense=None
        self._assert_expenditure_is_invalid

    def test_expense_cannot_be_zero(self):
        self.expenditure.expense=0
        self._assert_expenditure_is_invalid

    def test_image_can_be_blank(self):
        self.expenditure.image=None
        self._assert_expenditure_is_valid

    def test_title_cannot_be_blank(self):
        self.expenditure.title=""
        self._assert_expenditure_is_invalid

    def test_description_cannot_be_blank(self):
        self.expenditure.description=""
        self._assert_expenditure_is_invalid

    def _assert_expenditure_is_valid(self):
        try:
            self.expenditure.full_clean()
        except (ValidationError):
            self.fail('Test invoice should be valid')
    
    def _assert_expenditure_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.expenditure.full_clean()