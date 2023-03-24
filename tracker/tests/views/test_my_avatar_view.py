from django.test import TransactionTestCase, Client
from django.urls import reverse
from tracker.models import User, Level, UserLevel, Activity, Achievement, UserAchievement
from tracker.tests.helpers import delete_avatar_after_test

class MyAchievementsViewTests(TransactionTestCase):

    fixtures = ['tracker/tests/fixtures/default_user.json']

    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(email='galin@email.com')
        self.level = Level.objects.create(name='level', description='description', required_points=10)
        self.userlevel = UserLevel.objects.create(user=self.user, level=self.level, points=1000)
        self.achievement = Achievement.objects.create(name="Avatar master", description="Test", criteria="Test", badge="Test")
        self.url = reverse('my_avatar')

    def test_view_requires_authentication(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        delete_avatar_after_test(self)

    def test_view_uses_correct_template(self):
        self.userlevel.delete()
        UserLevel.objects.create(user=self.user, level=self.level, points=0)
        self.client.login(email='galin@email.com', password='Password123')
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'my_avatar.html')
        delete_avatar_after_test(self)

    def test_correct_context(self):
        self.client.login(email='galin@email.com', password='Password123')
        response = self.client.get(self.url)
        self.assertIn('components', response.context)
        self.assertIn('colours', response.context)
        self.assertIn('locked_items', response.context)
        self.assertIn('tier_info', response.context)
        self.assertIn('user_tier_colour', response.context)
        self.assertEqual(response.status_code, 200)
        delete_avatar_after_test(self)

    def test_with_random(self):
        self.client.login(email='galin@email.com', password='Password123')
        response = self.client.get(self.url, {'random': ''})
        self.assertEqual(response.status_code, 200)
        delete_avatar_after_test(self)

    def test_with_clear(self):
        self.client.login(email='galin@email.com', password='Password123')
        response = self.client.get(self.url, {'clear': ''})
        self.assertEqual(response.status_code, 200)
        delete_avatar_after_test(self)

    def test_already_edited_before(self):
        Activity.objects.create(user=self.user, name="You've created an avatar")
        self.client.login(email='galin@email.com', password='Password123')
        response = self.client.get(self.url, {'random': ''})
        self.assertEqual(response.status_code, 200)
        delete_avatar_after_test(self)

    def test_deleted_avatar_template(self):
        self.client.login(email='galin@email.com', password='Password123')
        response = self.client.get(self.url, {'random': ''})
        self.assertEqual(response.status_code, 200)
        delete_avatar_after_test(self)
        response = self.client.get(self.url, {'random': ''})
        self.assertEqual(response.status_code, 200)
        delete_avatar_after_test(self)

    def test_unlock_avatar(self):
        url = reverse('unlock_avatar') + "?eyewear=sunglasses&tier=silver"
        self.client.login(email='galin@email.com', password='Password123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_unlock_avatar_with_no_arguments(self):
        url = reverse('unlock_avatar')
        self.client.login(email='galin@email.com', password='Password123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
    def test_unlock_avatar_with_wrong_category(self):
        url = reverse('unlock_avatar') + "?hair=sunglasses&tier=silver"
        self.client.login(email='galin@email.com', password='Password123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_deleted_avatar_master_achievement(self):
        self.achievement.delete()
        self.client.login(email='galin@email.com', password='Password123')
        response = self.client.get(self.url, {'random': ''})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(UserAchievement.objects.filter(user=self.user, achievement=self.achievement).count(), 0)
        delete_avatar_after_test(self)

    def test_avatar_master_not_given_twice(self):
        self.client.login(email='galin@email.com', password='Password123')
        response = self.client.get(self.url, {'random': ''})
        self.assertEqual(response.status_code, 200)
        delete_avatar_after_test(self)
        self.assertEqual(UserAchievement.objects.filter(user=self.user, achievement=self.achievement).count(), 1)
        Activity.objects.get(user=self.user, name="You've created an avatar").delete()
        response = self.client.get(self.url, {'random': ''})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(UserAchievement.objects.filter(user=self.user, achievement=self.achievement).count(), 1)
        delete_avatar_after_test(self)
