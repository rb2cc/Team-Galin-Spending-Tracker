from django.test import TestCase, Client
from django.urls import reverse
from tracker.models import User, Category, Expenditure

"""Unit tests for the recover_category view"""
class RecoverCategoryViewTestCase(TestCase):

    fixtures = ['tracker/tests/fixtures/default_user.json',
                'tracker/tests/fixtures/default_category.json',
                'tracker/tests/fixtures/extra_categories.json']
    def setUp(self):
        self.client = Client()
        self.url = reverse('recover_category')
        self.user = User.objects.get(email='james@example.org')
        self.cat_one = Category.objects.get(name='Test')
        self.cat_two = Category.objects.get(name='Test2')
        self.cat_three = Category.objects.get(name='Test3')
        self.overall_cat = Category.objects.get(name='Test4')

    def test_recover_category_post_request(self):
        self.user.available_categories.add(self.cat_one, self.cat_two, self.cat_three, self.overall_cat)
        Expenditure.objects.create(
            category=self.cat_one,
            title='Test Expenditure',
            description='This is a test expenditure',
            expense=50,
            user=self.user
        )
        self.client.login(email='james@example.org', password='Lu123')
        response = self.client.post(reverse('bin_category', kwargs={'id': 0}))
        self.assertEqual(response.status_code, 302)
        response = self.client.post(self.url, {'radio_pk': self.cat_one.id})
        self.assertFalse(self.cat_one.is_binned)
        self.assertEqual(response.status_code, 302)

    def test_recover_category_without_radio_pk(self):
        self.client.login(email='james@example.org', password='Lu123')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)

    def test_recover_category_get_request(self):
        self.client.login(email='james@example.org', password='Lu123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
