from django.test import TestCase, Client
from django.urls import reverse
from tracker.models import User, Post, Comment, Forum_Category
from tracker.forms import PostForm

class CreatePostViewTests(TestCase):

    fixtures = ['tracker/tests/fixtures/default_user.json']

    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(email='galin@email.com')
        self.forum_category = Forum_Category.objects.create(title='Test Category', slug='test-category', description='Description')
        self.url = reverse('create_post')

    def test_create_post_url(self):
        self.client.login(email='galin@email.com', password='Password123')
        self.assertEqual(self.url, '/create_post/')

    def test_posts_view_uses_correct_template(self):
        self.client.login(email='galin@email.com', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forum/create_post.html')

    def test_correct_context(self):
        self.client.login(email='galin@email.com', password='Password123')
        response = self.client.get(self.url)
        self.assertIn('form', response.context)
        self.assertIn('title', response.context)

    def test_get_request_correct_form(self):
        self.client.login(email='galin@email.com', password='Password123')
        response = self.client.get(self.url)
        self.assertIsInstance(response.context['form'], PostForm)

    def test_post_request_with_valid_data_creates_new_post(self):
        self.client.login(email='galin@email.com', password='Password123')
        data = {
            'title': 'Test Title',
            'content': 'Test Content',
            'forum_categories': self.forum_category.id,
            'media': ''
        }
        response = self.client.post(self.url, data)
        self.assertTrue(Post.objects.filter(title='Test Title', content='Test Content', user=self.user).exists())
        self.assertRedirects(response, reverse('forum_home'))

    def test_post_request_with_invalid_data_does_not_create_new_post(self):
        self.client.login(email='galin@email.com', password='Password123')
        data = {
            'title': 'Test Title',
            'content': 'Test Content',
            'forum_categories': '',
            'media': ''
        }
        response = self.client.post(self.url, data)
        self.assertFalse(Post.objects.filter(title='Test Title', content='Test Content', user=self.user).exists())
