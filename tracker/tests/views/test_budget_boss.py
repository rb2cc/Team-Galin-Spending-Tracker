from django.test import TestCase
from django.urls import reverse
from tracker.models import User, Category, Achievement, UserAchievement, Activity
from tracker.forms import AddCategoryForm
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError

class TestBudgetBoss(TestCase):
    def setUp(self):
        self.url = reverse('category_list')
        self.user = User.objects.create_user(
            email='james@example.org',
            first_name='James',
            last_name='Lu',
            password='Lu123',
        )
        self.form_input = {
            'name': 'New',
            'week_limit': 50
        }
        self.achievement = Achievement.objects.create(name="Budget boss", description="Test", criteria="Test", badge="Test")
        overall_category = Category.objects.create(name='Overall',week_limit=100, is_overall=True)
        self.user.available_categories.add(overall_category)

    def test_budget_boss_achievement(self):
        self.client.login(username=self.user.email, password='Lu123')
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        user_achievement = UserAchievement.objects.filter(user=self.user, achievement=self.achievement)
        self.assertTrue(user_achievement.exists())
        user_activity = Activity.objects.filter(user=self.user, name="You've earned \"Budget boss\" achievement", points=15)
        self.assertTrue(user_activity.exists())

    def test_budget_boss_achievement_object_does_not_exist(self):
        self.client.login(username=self.user.email, password='Lu123')
        self.achievement.delete()
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        with self.assertRaises(ObjectDoesNotExist):
            Achievement.objects.get(name="Budget boss")

