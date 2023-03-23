from django.test import TestCase, Client
from django.urls import reverse
from tracker.models import Post, User

"""Unit tests for the forum_home view"""
class ForumHomeTestCase(TestCase):
    
    fixtures = ['tracker/tests/fixtures/default_user.json']
    

    def setUp(self):
        self.user = User.objects.get(email = 'james@example.org')
        self.url = reverse('forum_home')

    def test_url(self):
        self.assertEqual(self.url, '/forum_home/')

    def test_successful_render(self):
        self.client.login(username = self.user.email, password = 'Lu123')
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'forum/forum_home.html')

    def test_correct_context(self):
        self.client.login(username = self.user.email, password = 'Lu123')
        response = self.client.get(self.url)
        self.assertIn('all_forum_categories', response.context)
        self.assertIn('num_posts', response.context)
        self.assertIn('num_users', response.context)
        self.assertIn('num_categories', response.context)
        self.assertIn('last_post', response.context)
        self.assertIn('title', response.context)

    def test_no_post_object(self):
        self.client.login(username = self.user.email, password = 'Lu123')
        response = self.client.get(self.url)
        self.assertEqual(response.context['last_post'], None)

    def test_with_post_object(self):
        Post.objects.create(user= self.user, title='abc', slug='xyz')
        self.client.login(username = self.user.email, password = 'Lu123')
        response = self.client.get(self.url)
        self.assertIsNotNone(response.context['last_post'])
