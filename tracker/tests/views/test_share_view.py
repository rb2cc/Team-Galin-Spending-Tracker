from django.test import TestCase, RequestFactory, Client
from django.urls import reverse
from tracker.models import User, UserAchievement, Achievement, Activity, UserChallenge, Challenge, UserLevel, Level
from tracker.views import share_avatar, share_challenge, share_achievement, share
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from tracker.views import handle_share
from tracker.tests.helpers import delete_avatar_after_test

class ShareViewsTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            email='testuser@example.com',
            first_name='Test',
            last_name='User',
            password='testpassword'
        )
        self.level = Level.objects.create(name="Level 1", description="Level 1 description", required_points=0)
        self.user_level = UserLevel.objects.create(user=self.user, level=self.level, points=0)
        self.achievement = Achievement.objects.create(
            name="First share",
            description="First share description",
            criteria="Share something for the first time",
            badge="images/first_share.png"
        )
        self.user_achievement = UserAchievement.objects.create(user=self.user, achievement=self.achievement)
        self.challenge = Challenge.objects.create(
            name="Test challenge",
            description="Test challenge description",
            points=100,
            start_date='2023-03-01',
            end_date='2023-03-31'
        )
        self.user_challenge = UserChallenge.objects.create(user=self.user, challenge=self.challenge)

    def test_share_avatar(self):
        request = self.factory.get(reverse('share_avatar'))
        request.user = self.user
        response = share_avatar(request)
        self.assertEqual(response.status_code, 200)

    def test_share_avatar_with_existing_template(self):
        self.client.login(email='testuser@example.com', password='testpassword')
        url = reverse('my_avatar')
        response = self.client.get(url, {'random': ''})
        self.assertEqual(response.status_code, 200)
        request = self.factory.get(reverse('share_avatar'))
        request.user = self.user
        response = share_avatar(request)
        self.assertEqual(response.status_code, 200)
        delete_avatar_after_test(self)

    def test_share_avatar_with_deleted_template(self):
        self.client.login(email='testuser@example.com', password='testpassword')
        url = reverse('my_avatar')
        response = self.client.get(url, {'random': ''})
        self.assertEqual(response.status_code, 200)
        delete_avatar_after_test(self)
        request = self.factory.get(reverse('share_avatar'))
        request.user = self.user
        response = share_avatar(request)
        self.assertEqual(response.status_code, 200)

    def test_share_challenge(self):
        request = self.factory.get(reverse('share_challenge', args=[str(self.user_challenge.id)]))
        request.user = self.user
        response = share_challenge(request, self.user_challenge.id)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.challenge.name, response.content.decode())

    def test_share_achievement(self):
        request = self.factory.get(reverse('share_achievement', args=[str(self.user_achievement.id)]))
        request.user = self.user
        response = share_achievement(request, self.user_achievement.id)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.achievement.name, response.content.decode())

    def test_share_nothing(self):
        self.client.login(email='testuser@example.com', password='testpassword')
        url = reverse('share')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_share_not_accepted_object(self):
        self.client.login(email='testuser@example.com', password='testpassword')
        request = self.factory.get(reverse('share'))
        request.user = self.user
        response = share(request, 1, 'x', 'x', 'x', 'x')
        self.assertEqual(response.status_code, 302)
