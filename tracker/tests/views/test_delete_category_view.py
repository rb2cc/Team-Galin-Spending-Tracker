from django.test import TestCase, Client
from django.urls import reverse
from tracker.models import User, Category

"""Unit tests for the recover_category view"""
class DeleteCategoryViewTestCase(TestCase):

    def setUp(self):
        self.c = Client()
        self.url = reverse('delete_category')
        self.user = User.objects.create(email='user@email.com', password='Password123')
        self.category = Category.objects.create(name = 'Category', week_limit = 10, is_binned=True)

    def test_url(self):
        self.assertEqual(self.url, '/delete_category')

    def test_successful_delete(self):
        self.c.login(email='user@email.com', password='Password123')
        before_count = Category.objects.count()
        response = self.c.post(self.url, {'radio_pk': self.category.pk})
        after_count = Category.objects.count()
        self.assertEqual(after_count, before_count-1)
        self.assertRedirects(response, reverse('category_bin'))
