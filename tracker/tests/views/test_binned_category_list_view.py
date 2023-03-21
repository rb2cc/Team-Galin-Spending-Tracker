from django.test import TestCase, Client
from django.urls import reverse
from tracker.models import User, Category

"""Unit tests for the binned_category_list view"""
class BinnedCategoryListViewTestCase(TestCase):

    def setUp(self):
        self.url = reverse('category_bin')

    def test_binned_category_url(self):
        self.assertEqual(self.url, '/category_bin/')

    def test_get_request(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'category_bin.html')
        self.assertIn('binned_categories', response.context)
