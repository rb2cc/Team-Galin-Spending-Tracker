from django.test import TestCase, RequestFactory
from django.urls import reverse
from tracker.models import User, UserAchievement, Achievement, Activity, UserChallenge, Challenge, UserLevel, Level
from tracker.views import share_avatar, share_challenge, share_achievement
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from tracker.views import handle_share
import os

class ShareViewsTestCase(TestCase):

    fixtures = ['tracker/tests/fixtures/default_user.json']

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.get(email='test@example.com')
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

