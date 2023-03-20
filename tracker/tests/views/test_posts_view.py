from django.test import TestCase, Client
from django.urls import reverse
from tracker.models import Post, User

"""Unit tests for the posts view"""
class PostsTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(email='user@email.com', password='Password123')
        self.post = Post.objects.create(user=self.user, title='test', slug='abc')
        self.url = reverse('posts')

    def test_posts_url(self):
        self.assertEqual(self.url, '/posts/')

    # def test_correct_render(self):
    #     response = self.client.get(self.url)
    #     assertTemplateUsed(response, 'forum/posts.html')

    # def test_correct_context(self):
    #     response = self.client.get(self.url, self.post.slug)
    #     self.assertIn('posts', response.context)
    #     self.assertIn('forum', response.context)
    #     self.assertIn('title', response.context)
