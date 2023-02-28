from django.test import TestCase
from django.urls import reverse
from tracker.models import User, Category
from tracker.forms import AddCategoryForm

"""Unit tests for edit_category view"""
class EditCategoryViewTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email = 'james@example.org',
            first_name='James',
            last_name = 'Lu',
            password = 'Lu123',
        )
        self.cat_one = Category.objects.create(id = 0, name = 'Test', week_limit = 100)
        self.cat_two = Category.objects.create(id = 1, name = 'Test2', week_limit = 150)
        self.url = reverse('edit_category', kwargs={'id': 0})
        self.form_input = {
            'name':'Changed Test',
            'week_limit': 150
        }

    def test_edit_category_url(self):
        self.assertEqual(self.url, '/edit_category/0')

    def test_post_edit_category(self):
        self.user.available_categories.add(self.cat_one, self.cat_two)
        self.client.login(username = self.user.email, password = 'Lu123')
        before_count = Category.objects.count()
        response = self.client.post(self.url, self.form_input, follow = True)
        after_count = Category.objects.count()
        self.assertEqual(after_count, before_count)
        remaining = list(map(lambda category: category.name, list(Category.objects.all())))
        self.assertFalse('Test' in remaining)
        self.assertTrue('Changed Test' in remaining)
        self.assertRedirects(response, reverse('category_list'), status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'category_list.html')

    def test_get_edit_category(self):
        self.user.available_categories.add(self.cat_one, self.cat_two)
        self.client.login(username = self.user.email, password = 'Lu123')
        response = self.client.get(self.url)
        form = response.context['form']
        self.assertEqual(form.instance, self.cat_one)
        self.assertTrue(isinstance(form, AddCategoryForm))
        self.assertTemplateUsed(response, 'edit_category.html')


