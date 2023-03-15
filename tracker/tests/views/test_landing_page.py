from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from tracker.models import Expenditure, Activity, UserAchievement, Achievement
from tracker.models import Level, UserLevel
from tracker.forms import ExpenditureForm
from tracker.models import User
from tracker.models import Category
from tracker.views import getDateListAndDailyExpenseList
from django.utils import timezone



class LandingPageViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpassword'
        )
        self.category = Category.objects.create(name='Test Category',week_limit=100)
        self.user.available_categories.add(self.category)
        self.user.save()
        self.url = reverse('landing_page')
        self.client.login(email='testuser@example.com', password='testpassword')

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

    def test_progress_percentage_100(self):
        level = Level.objects.create(name="Level 1", description="Description of level 1", required_points=100)
        user_level = UserLevel.objects.create(user=self.user, level=level, points=100)
        response = self.client.get(self.url)
        self.assertEqual(response.context['progress_percentage'], 100)

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




