from django.test import TestCase, Client
from django.urls import reverse
from tracker.models import User, Category, Expenditure

"""Unit tests for the category_progress view"""
class CategoryProgressViewTestCase(TestCase):
    fixtures = ['tracker/tests/fixtures/default_user.json',
                'tracker/tests/fixtures/default_category.json',
                'tracker/tests/fixtures/extra_categories.json']

    def setUp(self):
        self.client = Client()
        self.url = reverse('category_progress', kwargs={'offset': 0})
        self.user = User.objects.get(email='james@example.org')
        self.cat_one = Category.objects.get(name='Test')
        self.cat_two = Category.objects.get(name='Test2')
        self.cat_three = Category.objects.get(name='Test3')
        self.overall_cat = Category.objects.get(name='Test4')

    def test_category_progress_get_request(self):
        self.user.available_categories.add(self.cat_one, self.cat_two, self.cat_three, self.overall_cat)
        test_expenditure = Expenditure.objects.create(
            category=self.cat_one,
            title='Test Expenditure',
            description='This is a test expenditure',
            expense=0,
            user=self.user
        )
        self.client.login(email='james@example.org', password='Lu123')
        for expense in [60, 90, 150]:
            test_expenditure.expense = expense
            test_expenditure.save()
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 200)

    def test_category_progress_with_positive_offset(self):
        self.user.available_categories.add(self.cat_one, self.cat_two, self.cat_three, self.overall_cat)
        self.client.login(email='james@example.org', password='Lu123')
        url = reverse('category_progress', kwargs={'offset': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)