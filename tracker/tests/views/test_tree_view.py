from django.test import Client, TransactionTestCase
from django.urls import reverse
from tracker.models import User, Level, UserLevel, Tree, Achievement, UserAchievement
from django.contrib.messages import get_messages
import json


class GardenViewTestCase(TransactionTestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpassword',
            first_name='Test',
            last_name='User'
        )
        self.level = Level.objects.create(
            name='Test Level',
            description='This is a test level',
            required_points=100
        )
        self.user_level = UserLevel.objects.create(
            user=self.user,
            level=self.level,
            points=550
        )
        self.tree = Tree.objects.create(user=self.user, x_position=500, y_position=50)
        self.achievement = Achievement.objects.create(name="Planting pioneer", description="Test", criteria="Test", badge="Test")

    def test_garden_view_get(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('garden'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.tree, response.context['trees'])

    def test_garden_view_post_enough_points(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('garden'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Tree.objects.filter(user=self.user).count(), 2)

    def test_garden_view_post_not_enough_points(self):
        self.client.force_login(self.user)
        self.user_level.points = 50
        self.user_level.save()
        response = self.client.post(reverse('garden'))
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Not Enough Points Available')

    def test_deleted_garden_achievement(self):
        self.achievement.delete()
        self.tree.delete()
        self.client.force_login(self.user)
        response = self.client.post(reverse('garden'))
        self.assertEqual(response.status_code, 200)

    def test_garden_user_achievement_already_exists(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('garden'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(UserAchievement.objects.filter(user=self.user, achievement=self.achievement).count(), 1)
        self.user.trees = 0
        self.user.save()
        response = self.client.post(reverse('garden'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(UserAchievement.objects.filter(user=self.user, achievement=self.achievement).count(), 1)
