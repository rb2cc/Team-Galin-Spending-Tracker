from django.test import TestCase, Client
from django.urls import reverse
from tracker.models import User, Category

"""Unit tests for the binned_category_list view"""
class BinnedCategoryListViewTestCase(TestCase):
    
    fixtures = ['tracker/tests/fixtures/default_user.json',
                'tracker/tests/fixtures/default_category.json']
    
    def setUp(self):
        self.url = reverse('category_bin')
        self.user = User.objects.get(email='james@example.org')
        self.category = Category.objects.get(name='Test')

    def test_binned_category_url(self):
        self.assertEqual(self.url, '/category_bin/')

    def test_get_request(self):
        self.client.login(email='james@example.org', password='Lu123')
        self.category.is_binned = True
        self.category.save()
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'category_bin.html')
        self.assertIn('binned_categories', response.context)
        self.assertEqual(response.status_code, 200)
        