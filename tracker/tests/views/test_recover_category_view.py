from django.test import TestCase, Client
from django.urls import reverse
from tracker.models import User, Category

"""Unit tests for the recover_category view"""
class RecoverCategoryViewTestCase(TestCase):

    def setUp(self):
        self.c = Client()
        self.url = reverse('recover_category')
        self.user = User.objects.create(email='user@email.com', password='Password123')
        self.category = Category.objects.create(name = 'Category', week_limit = 10, is_binned=True)

    def test_url(self):
        self.assertEqual(self.url, '/recover_category')

    
