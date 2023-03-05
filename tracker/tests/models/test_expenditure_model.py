from django.core.exceptions import ValidationError
from django.test import TestCase
from tracker.models import User, Category, Expenditure


"""Unit tests for the expenditure model"""
class ExpenditureModelTestCase(TestCase):

    fixtures = ['tracker/tests/fixtures/default_user.json']

    def setUp(self):

        url = 'test_image/fortlobby.png'

        self.user = User.objects.get(email = 'james@example.org')

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
        self._assert_expenditure_is_invalid()

    def test_expense_cannot_be_more_than_20_digits(self):
        self.expenditure.expense=1000000000000000000.00
        self._assert_expenditure_is_invalid()

    def test_expense_cannot_have_more_than_2_decimal_places(self):
        self.expenditure.expense=100.555
        self._assert_expenditure_is_invalid()

    def test_expense_cannot_be_blank(self):
        self.expenditure.expense=None
        self._assert_expenditure_is_invalid()

    def test_expense_cannot_be_zero(self):
        self.expenditure.expense=0
        self._assert_expenditure_is_invalid()

    def test_image_can_be_blank(self):
        self.expenditure.image=None
        self._assert_expenditure_is_valid()

    def test_title_cannot_be_blank(self):
        self.expenditure.title=""
        self._assert_expenditure_is_invalid()

    def test_title_cannot_be_more_than_25_characters(self):
        self.expenditure.title = "x"*26
        self._assert_expenditure_is_invalid

    def test_description_cannot_be_blank(self):
        self.expenditure.description=""
        self._assert_expenditure_is_invalid()

    def test_description_cannot_be_more_than_280_characters(self):
        self.expenditure.description="x"*281
        self._assert_expenditure_is_invalid()
        
    def test_is_binned_boolean_cannot_be_null(self):
        self.expenditure.is_binned=None
        self._assert_expenditure_is_invalid()
        
    def test_is_binned_boolean_can_be_true(self):
        self.expenditure.is_binned=True
        self._assert_expenditure_is_valid()
        
    def test_is_binned_boolean_is_default_false(self):
        if self.expenditure.is_binned==False:
            self._assert_expenditure_is_valid()

    def _assert_expenditure_is_valid(self):
        try:
            self.expenditure.full_clean()
        except (ValidationError):
            self.fail('Test expenditure should be valid')
    
    def _assert_expenditure_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.expenditure.full_clean()