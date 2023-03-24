from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from tracker.models import Expenditure, Activity, UserAchievement, Achievement
from tracker.models import Level, UserLevel
from tracker.forms import ExpenditureForm
from tracker.models import User
from tracker.models import Category
from tracker.views import getDateListAndDailyExpenseList, landing_page
from django.utils import timezone
from django.test import TestCase, TransactionTestCase
from tracker.tests.helpers import delete_avatar_after_test
from datetime import timedelta
from django.utils import timezone

class LandingPageViewTest(TransactionTestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpassword'
        )
        self.superuser = User.objects.create_superuser(email='superuser@email.com', password='Password123')
        self.staff = User.objects.create_user(email='staff@email.com', password='Password123', is_staff = True)
        self.category_overall = Category.objects.create(name='Overall',week_limit=100, is_overall=True)
        self.category = Category.objects.create(name='Test Category',week_limit=100)
        self.user.available_categories.add(self.category_overall)
        self.user.available_categories.add(self.category)
        self.user.save()
        self.url = reverse('landing_page')
        self.client.login(email='testuser@example.com', password='testpassword')
        self.achievement = Achievement.objects.create(name="First expenditure", description="Test", criteria="Test", badge="Test")
        self.user_achievement = UserAchievement.objects.create(user=self.user, achievement=self.achievement)
        self.level = Level.objects.create(name='level', description='description', required_points=100)
        self.user_level = UserLevel.objects.create(user=self.user, level=self.level, points=1000)

    def test_landing_page_post_request(self):
        data = {
            'title': 'Test Expenditure',
            'category': self.category.id,
            'expense': 100.0,
            'description': 'Test description',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(Expenditure.objects.filter(user=self.user).count(), 1)
        activity_name = f'You\'ve created a "Test Expenditure" expenditure of "{self.category.name}" category with 100.0 expense'
        self.assertEqual(Activity.objects.filter(user=self.user, name=activity_name).count(), 1)
        self.assertRedirects(response, self.url)

    def test_landing_page_post_request_percent_greater_than_100(self):
        data = {
            'title': 'Test Expenditure',
            'category': self.category.id,
            'expense': 200.0,
            'description': 'Test description',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(Expenditure.objects.filter(user=self.user).count(), 1)
        activity_name = f'You\'ve created a "Test Expenditure" expenditure of "{self.category.name}" category with 200.0 expense'
        self.assertEqual(Activity.objects.filter(user=self.user, name=activity_name).count(), 1)
        self.assertRedirects(response, self.url)

    def test_landing_page_post_request_percent_less_than_90_and_email_sent(self):
        self.user.has_email_sent = True
        self.user.save()
        data = {
            'title': 'Test Expenditure',
            'category': self.category.id,
            'expense': 80,
            'description': 'Test description',
        }
        response = self.client.post(self.url, data)
        self.assertRedirects(response, self.url)

    def test_landing_page_post_request_percent_greater_than_90_and_email_sent(self):
        self.user.has_email_sent = True
        self.user.save()
        data = {
            'title': 'Test Expenditure',
            'category': self.category.id,
            'expense': 95,
            'description': 'Test description',
        }
        response = self.client.post(self.url, data)
        self.assertRedirects(response, self.url)

    def test_progress_percentage_100(self):
        self.user_level.points = 100
        self.user_level.save()
        response = self.client.get(self.url)
        self.assertEqual(response.context['progress_percentage'], 100)

    def test_progress_percentage_95(self):
        self.user_level.points = 95
        self.user_level.save()
        response = self.client.get(self.url)
        self.assertEqual(response.context['progress_percentage'], 95)

    def test_get_date_list_and_daily_expense_list(self):
        date_created = timezone.now().date()
        Expenditure.objects.create(
            user=self.user,
            title='Expenditure 1',
            category=self.category,
            expense=100,
            date_created=date_created,
        )
        Expenditure.objects.create(
            user=self.user,
            title='Expenditure 2',
            category=self.category,
            expense=200,
            date_created=date_created,
        )
        object_list = Expenditure.objects.filter(user=self.user, is_binned=False)
        date_list, daily_expense_list = getDateListAndDailyExpenseList(object_list, 7)
        self.assertEqual(len(date_list), 7)
        self.assertEqual(len(daily_expense_list), 7)
        self.assertEqual(date_list[6], date_created)
        self.assertEqual(daily_expense_list[6], 300)

    def test_first_expenditure_user_achievement_exists(self):
        self.user_achievement.delete()
        Expenditure.objects.create(
            user=self.user,
            title='Test Expenditure',
            category=self.category,
            expense=100
        )
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(UserAchievement.objects.filter(user=self.user).count(), 1)
        self.assertEqual(Expenditure.objects.filter(user=self.user).count(), 1)

    def test_first_expenditure_achievement_deleted(self):
        self.user_achievement.delete()
        self.achievement.delete()
        Expenditure.objects.create(
            user=self.user,
            title='Test Expenditure',
            category=self.category,
            expense=100
        )
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(UserAchievement.objects.filter(user=self.user).count(), 0)
        self.assertEqual(Expenditure.objects.filter(user=self.user).count(), 1)

    def test_first_expenditure_achievement_not_given_twice(self):
        Expenditure.objects.create(
            user=self.user,
            title='Test Expenditure',
            category=self.category,
            expense=100
        )
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(UserAchievement.objects.filter(user=self.user).count(), 1)
        self.assertEqual(Expenditure.objects.filter(user=self.user).count(), 1)

    def test_not_same_date(self):
        exp1 = Expenditure.objects.create(
            user=self.user,
            title='Test Expenditure',
            category=self.category,
            expense=100,
            date_created = timezone.now() - timezone.timedelta(days=2)
        )
        exp2 = Expenditure.objects.create(
            user=self.user,
            title='Test Expenditure 2',
            category=self.category,
            expense=100,
            date_created = timezone.now() - timezone.timedelta(days=1)
        )
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)


    def test_landing_page_with_existing_avatar_template(self):
        url = reverse('my_avatar')
        response = self.client.get(url, {'random': ''})
        self.assertEqual(response.status_code, 200)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        delete_avatar_after_test(self)

    def test_landing_page_with_deleted_avatar_template(self):
        url = reverse('my_avatar')
        response = self.client.get(url, {'random': ''})
        self.assertEqual(response.status_code, 200)
        delete_avatar_after_test(self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_landing_page_with_deleted_user_level(self):
        self.user_level.delete()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
