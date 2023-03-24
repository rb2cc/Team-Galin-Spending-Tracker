from django.test import Client, TestCase
from django.urls import reverse
from tracker.models import User, Level, UserLevel, Tree
from django.contrib.messages import get_messages
import json


class GardenViewTestCase(TestCase):
    
    fixtures = ['tracker/tests/fixtures/default_user.json']
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(email='test@example.com')
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
