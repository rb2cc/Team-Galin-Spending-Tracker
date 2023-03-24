from django.test import TestCase
from django.urls import reverse
from tracker.models import User, Category

"""Unit tests for the bin_category view"""
class BinCategoryViewTestCase(TestCase):

    fixtures = ['tracker/tests/fixtures/default_user.json',
                'tracker/tests/fixtures/default_category.json',
                'tracker/tests/fixtures/extra_categories.json']

    def setUp(self):
        self.user = User.objects.get(email = 'james@example.org')
        self.cat_one = Category.objects.get(name = 'Test')
        self.cat_two = Category.objects.get(name = 'Test2')
        self.cat_three = Category.objects.get(name = 'Test3')
        self.overall_cat = Category.objects.get(name = 'Test4')
        self.url = reverse('bin_category', kwargs={'id': 0})

    def test_bin_category_url(self):
        self.assertEqual(self.url, '/bin_category/0')

    def test_remove_category_view_removes_category(self):
        self.user.available_categories.add(self.cat_one, self.cat_two, self.cat_three, self.overall_cat)
        self.client.login(username = self.user.email, password = 'Lu123')
        before_count = Category.objects.count()
        response = self.client.post(self.url)
        after_count = Category.objects.filter(is_binned=False).count()
        self.assertEqual(after_count, before_count-1)
        remaining = list(map(lambda category: category.name, list(Category.objects.filter(is_binned=False))))
        self.assertFalse('Test' in remaining)
        self.assertRedirects(response, reverse('category_list'), status_code=302, target_status_code=200)

    def test_bin_category_is_global(self):
        self.cat_one.is_global = True
        self.cat_one.save()
        self.user.available_categories.add(self.cat_one, self.cat_two, self.cat_three, self.overall_cat)
        self.client.login(username=self.user.email, password='Lu123')
        before_count = Category.objects.count()
        response = self.client.post(self.url)
        after_count = Category.objects.filter(is_binned=False).count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 302)
