from django.test import TestCase
from decimal import Decimal
from math import floor
from tracker.models import User, UserLevel, Level, Activity
from tracker.views import update_user_level

class UpdateUserLevelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(email="test@example.com", first_name="Test", last_name="User")
        self.user.set_password("testpassword")
        self.user.save()
        level = Level.objects.create(name="Level 1", description="Description of level 1", required_points=0)
        UserLevel.objects.create(user=self.user, level=level, points=0)

    def test_update_user_level_same_level(self):
        update_user_level(self.user)
        user_level = UserLevel.objects.get(user=self.user)
        self.assertEqual(user_level.level.name, "Level 1")

    def test_update_user_level_level_up(self):
        user_level = UserLevel.objects.get(user=self.user)
        user_level.points = 100
        user_level.save()
        update_user_level(self.user)
        user_level.refresh_from_db()
        self.assertEqual(user_level.level.name, "Level 2")

    def test_update_user_level_level_up_with_new_levels(self):
        user_level = UserLevel.objects.get(user=self.user)
        user_level.points = 500
        user_level.save()
        update_user_level(self.user)
        user_level.refresh_from_db()
        self.assertEqual(user_level.level.name, "Level 6")

    def test_update_user_level_activity_creation(self):
        user_level = UserLevel.objects.get(user=self.user)
        user_level.points = 200
        user_level.save()
        update_user_level(self.user)
        user_activity = Activity.objects.filter(user=self.user, name="You've leveled up to Level 3")
        self.assertEqual(user_activity.count(), 1)