from django.test import TestCase
from django.urls import reverse
from tracker.models import User, Category, Achievement, Expenditure
from tracker.forms import AddCategoryForm

from django.utils import timezone
from dateutil.relativedelta import relativedelta, MO, SU
from datetime import timedelta, datetime

"""Unit tests for the category_progress view"""
class CategoryProgressViewTestCase(TestCase):

    fixtures = ['tracker/tests/fixtures/default_user.json',
                'tracker/tests/fixtures/default_category.json',
                'tracker/tests/fixtures/extra_categories.json',
                'tracker/tests/fixtures/default_expenditure.json']

    def setUp(self):
        self.user = User.objects.get(email = 'james@example.org')
        self.cat_one = Category.objects.get(name = 'Test')
        self.cat_two = Category.objects.get(name = 'Test2')
        self.cat_three = Category.objects.get(name = 'Test3')
        self.cat_overall = Category.objects.get(name = 'Test4')
        self.cat1_exp = Expenditure.objects.get(title = 'cat_one exp')
        self.cat2_exp = Expenditure.objects.get(title = 'cat_two exp')
        self.cat3_exp = Expenditure.objects.get(title = 'cat_three exp')
        self.user.available_categories.add(self.cat_one, self.cat_two, self.cat_three, self.cat_overall)
        self.url = reverse('category_progress', kwargs={'offset':0})

    def test_category_progress_url(self):
        self.assertEqual(self.url, '/category_progress/0')

    def test_correct_percent_calculated(self):
        self.client.login(username = self.user.email, password = 'Lu123')
        response = self.client.get(self.url)
        val_dict = response.context['cat_map']
        self.assertEqual(val_dict[self.cat_one.name][0], 50)
        self.assertEqual(val_dict[self.cat_two.name][0], 83)
        self.assertEqual(val_dict[self.cat_three.name][0], 5)
        self.assertEqual(response.context['overall_percent'], 37)

    def test_correct_colour_assigned(self):
        self.client.login(username = self.user.email, password = 'Lu123')
        response = self.client.get(self.url)
        val_dict = response.context['cat_map']
        self.assertEqual(val_dict[self.cat_one.name][1], "#118DD5")
        self.assertEqual(val_dict[self.cat_two.name][1], "#F2B933")
        self.assertEqual(val_dict[self.cat_three.name][1], "#4CAF50")
        self.assertEqual(response.context['overall_colour'], "#4CAF50")

    def test_offset_aligns_to_correct_week(self):
        self.client.login(username = self.user.email, password = 'Lu123')
        response = self.client.get(self.url)
        previous_week_response = self.client.get(reverse('category_progress', kwargs={'offset':response.context['prev']}))
        self.assertFalse(response == previous_week_response)
        current_monday = timezone.now().date() + relativedelta(weekday=MO(-1))
        current_sunday = current_monday + timedelta(days = 6)
        self.assertEqual(response.context['start'], current_monday)
        self.assertEqual(response.context['end'], current_sunday)
        prev_monday = current_monday - timedelta(days = 7)
        prev_sunday = prev_monday + timedelta(days = 6)
        self.assertEqual(previous_week_response.context['start'], prev_monday)
        self.assertEqual(previous_week_response.context['end'], prev_sunday)
        self.assertEqual(current_monday.weekday(), 0)
        self.assertEqual(current_sunday.weekday(), 6)
        self.assertEqual(prev_monday.weekday(), 0)
        self.assertEqual(prev_sunday.weekday(), 6)

    def test_info_correct_on_week_by_week_basis(self):
        self.client.login(username = self.user.email, password = 'Lu123')
        response = self.client.get(self.url)
        previous_week_response = self.client.get(reverse('category_progress', kwargs={'offset':response.context['prev']}))
        self.assertEqual(response.context['cat_map'][self.cat_one.name][0], 50)
        self.assertEqual(previous_week_response.context['cat_map'][self.cat_one.name][0], 0)
        new_exp = Expenditure.objects.create(
            category = self.cat_one,
            title = "Extra",
            description = "Extra",
            expense = 90,
            date_created = timezone.now().date() + relativedelta(weekday=MO(-2)),
            user = self.user
        )
        response = self.client.get(self.url)
        previous_week_response = self.client.get(reverse('category_progress', kwargs={'offset':response.context['prev']}))
        self.assertEqual(response.context['cat_map'][self.cat_one.name][0], 50)
        self.assertEqual(previous_week_response.context['cat_map'][self.cat_one.name][0], 90)