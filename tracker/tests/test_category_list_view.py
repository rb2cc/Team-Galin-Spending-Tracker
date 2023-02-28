from django.test import TestCase
from django.urls import reverse
from tracker.models import User, Category
from tracker.forms import AddCategoryForm

class CategoryListViewTestCase(TestCase):

    def setUp(self):
        self.url = reverse('category_list')
        self.user = User.objects.create_user(
            email = 'james@example.org',
            first_name='James',
            last_name = 'Lu',
            password = 'Lu123',
        )
        self.form_input = {
            'name':'New',
            'week_limit':50
        }

    def test_category_list_url(self):
        self.assertEqual(self.url, '/category_list')

    def test_get_category_list(self):
        cat_one = Category.objects.create(name = 'Test', week_limit = 100)
        cat_two = Category.objects.create(name = 'Test2', week_limit = 150)
        cat_three = Category.objects.create(name = 'Test3', week_limit = 200)
        self.user.available_categories.add(cat_one, cat_two, cat_three)
        self.client.login(username = self.user.email, password = 'Lu123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'category_list.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, AddCategoryForm))
        self.assertFalse(form.is_bound)
        category_list = list(response.context['categories'])
        self.assertEqual(len(category_list),3)

    def test_valid_add_category(self):
        self.client.login(username = self.user.email, password = 'Lu123')
        other_user = User.objects.create_user(
            email = 'johndoe@example.org',
            first_name='John',
            last_name = 'Doe',
            password = 'Doe123',
        )
        before_count = Category.objects.count()
        correct_user_before_count = self.user.available_categories.count()
        incorrect_user_before_count = other_user.available_categories.count()
        self.client.post(self.url, self.form_input, follow=True)
        after_count = Category.objects.count()
        correct_user_after_count = self.user.available_categories.count()
        incorrect_user_after_count = other_user.available_categories.count()
        self.assertEqual(after_count, before_count+1)
        self.assertEqual(correct_user_after_count, correct_user_before_count+1)
        self.assertEqual(incorrect_user_after_count, incorrect_user_before_count)

