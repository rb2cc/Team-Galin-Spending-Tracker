from django.test import TestCase
from django.urls import reverse
from tracker.models import User, Category

"""Unit tests for the remove_category view"""
class RemoveCategoryViewTestCase(TestCase):

    fixtures = ['tracker/tests/fixtures/default_user.json',
                'tracker/tests/fixtures/default_category.json',
                'tracker/tests/fixtures/extra_categories.json']

    def setUp(self):
        self.user = User.objects.get(email = 'james@example.org')
        self.cat_one = Category.objects.get(name = 'Test')
        self.cat_two = Category.objects.get(name = 'Test2')
        self.cat_three = Category.objects.get(name = 'Test3')
        self.overall_cat = Category.objects.get(name = 'Test4')
        self.url = reverse('remove_category', kwargs={'id': 0})

    def test_remove_category_url(self):
        self.assertEqual(self.url, '/remove_category/0')

    def test_remove_category_view_removes_category(self):
        self.user.available_categories.add(self.cat_one, self.cat_two, self.cat_three, self.overall_cat)
        self.client.login(username = self.user.email, password = 'Lu123')
        before_count = Category.objects.count()
        response = self.client.post(self.url)
        after_count = Category.objects.count()
        self.assertEqual(after_count, before_count-1)
        remaining = list(map(lambda category: category.name, list(Category.objects.all())))
        self.assertFalse('Test' in remaining)
        self.assertRedirects(response, reverse('category_list'), status_code=302, target_status_code=200)
