from django.test import Client, TestCase
from django.urls import reverse
from tracker.views import report
from tracker.models import User, Category, Expenditure
from django.utils import timezone
from tracker.forms import ReportForm

class ReportViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpassword',
            first_name='Test',
            last_name='User'
        )
        self.category = Category.objects.create(name='TestCategory', week_limit=100)
        self.user.available_categories.add(self.category)
        self.expenditure = Expenditure.objects.create(
            user=self.user,
            category=self.category,
            title='Test Expenditure',
            description='This is a test expenditure',
            expense=20,
            date_created=timezone.now(),
            is_binned=False
        )

    def test_report_view(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('report'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.expenditure, response.context['expenditures'])
        self.assertEqual(response.context['total_expense'], 20)

    def test_report_view_post_valid_form(self):
        self.client.force_login(self.user)
        today = timezone.now().date()
        start_date = today - timezone.timedelta(days=10)
        end_date = today + timezone.timedelta(days=10)
        post_data = {
            'start_date': start_date,
            'end_date': end_date,
        }
        response = self.client.post(reverse('report'), data=post_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.expenditure, response.context['expenditures'])
        self.assertEqual(response.context['start_date'], start_date)
        self.assertEqual(response.context['end_date'], end_date)

    
