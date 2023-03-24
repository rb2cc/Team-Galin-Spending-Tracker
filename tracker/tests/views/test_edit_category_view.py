from django.test import TestCase
from django.urls import reverse
from tracker.models import User, Category
from tracker.forms import AddCategoryForm, EditOverallForm

"""Unit tests for edit_category view"""
class EditCategoryViewTestCase(TestCase):

    fixtures = ['tracker/tests/fixtures/default_user.json',
                'tracker/tests/fixtures/default_category.json',
                'tracker/tests/fixtures/extra_categories.json']

    def setUp(self):
        self.user = User.objects.get(email = 'james@example.org')
        self.cat_one = Category.objects.get(name = 'Test')
        self.cat_two = Category.objects.get(name = 'Test2')
        self.overall_cat = Category.objects.get(name = 'Test4')
        self.url = reverse('edit_category', kwargs={'id': 0})
        self.form_input = {
            'name':'Changed Test',
            'week_limit': 150
        }

    def test_edit_category_url(self):
        self.assertEqual(self.url, '/edit_category/0')

    def test_post_edit_category(self):
        self.user.available_categories.add(self.cat_one, self.cat_two, self.overall_cat)
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

    def test_get_edit_overall_category(self):
        self.user.available_categories.add(self.overall_cat)
        self.client.login(username = self.user.email, password = 'Lu123')
        response = self.client.get(reverse('edit_category', kwargs={'id': 3}))
        form = response.context['form']
        self.assertEqual(form.instance, self.overall_cat)
        self.assertTrue(isinstance(form, EditOverallForm))
        self.assertTemplateUsed(response, 'edit_category.html')

    def test_post_edit_overall_category(self):
        self.user.available_categories.add(self.overall_cat)
        self.client.login(username=self.user.email, password='Lu123')
        before_count = Category.objects.count()
        response = self.client.post(reverse('edit_category', kwargs={'id': 3}), {'week_limit': 150}, follow=True)
        after_count = Category.objects.count()
        self.assertEqual(after_count, before_count)
        remaining = list(map(lambda category: category.week_limit, list(Category.objects.all())))
        self.assertFalse('500' in remaining)
        self.assertRedirects(response, reverse('category_list'), status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'category_list.html')

    def test_post_edit_overall_category_invalid_form(self):
        self.user.available_categories.add(self.overall_cat)
        self.client.login(username=self.user.email, password='Lu123')
        response = self.client.post(reverse('edit_category', kwargs={'id': 3}), {'week_limit': -150}, follow=True)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertTrue(isinstance(form, EditOverallForm))
        self.assertIn("The overall limit cannot be less than the sum of other categories", response.content.decode())

    def test_post_edit_category_invalid_weekly_limit(self):
        self.user.available_categories.add(self.cat_one, self.cat_two, self.overall_cat)
        self.client.login(username=self.user.email, password='Lu123')
        response = self.client.post(self.url, {'name':'Changed Test', 'week_limit': -150}, follow=True)
        remaining = list(map(lambda category: category.name, list(Category.objects.all())))
        self.assertTrue('Test' in remaining)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertTrue(isinstance(form, AddCategoryForm))
        self.assertIn("Weekly limit cannot be negative", response.content.decode())
    def test_post_valid_edit_category_form_without_changing_name(self):
        self.user.available_categories.add(self.cat_one, self.cat_two, self.overall_cat)
        self.client.login(username=self.user.email, password='Lu123')
        response = self.client.post(self.url, {'name': self.cat_one.name, 'week_limit': 350}, follow=True)
        remaining = list(map(lambda category: category.name, list(Category.objects.all())))
        self.assertTrue('Test' in remaining)
        self.assertEqual(response.status_code, 200)
    def test_post_valid_edit_category_form_without_changing_limit(self):
        self.user.available_categories.add(self.cat_one, self.cat_two, self.overall_cat)
        self.client.login(username=self.user.email, password='Lu123')
        response = self.client.post(self.url, {'name': self.cat_one.name, 'week_limit': self.cat_one.week_limit}, follow=True)
        remaining = list(map(lambda category: category.name, list(Category.objects.all())))
        self.assertTrue('Test' in remaining)
        self.assertEqual(response.status_code, 200)

    def test_post_edit_overall_category_without_changing_name(self):
        self.user.available_categories.add(self.overall_cat)
        self.client.login(username=self.user.email, password='Lu123')
        response = self.client.post(reverse('edit_category', kwargs={'id': 3}), {'week_limit': self.overall_cat.week_limit}, follow=True)
        self.assertEqual(response.status_code, 200)


