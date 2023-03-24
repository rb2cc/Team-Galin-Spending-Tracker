from django.test import TestCase, Client, TransactionTestCase
from django.urls import reverse
from tracker.models import User, Post, Comment, Forum_Category, UserLevel, Level, Achievement, UserAchievement
from tracker.forms import PostForm

class CreatePostViewTests(TransactionTestCase):

    fixtures = ['tracker/tests/fixtures/default_user.json']

    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(email='galin@email.com')
        self.forum_category = Forum_Category.objects.create(title='Test Category', slug='test-category', description='Description')
        self.level = Level.objects.create(name='level', description='description', required_points=10)
        self.userlevel = UserLevel.objects.create(user=self.user, level=self.level, points=20)
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
        self.assertRedirects(response, Post.objects.get(title='Test Title', user=self.user).get_url())

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

    def test_forum_achievement_integrity_error(self):
        Achievement.objects.create(name="Junior forumite", description="Test", criteria="Test", badge="Test")
        UserAchievement.objects.create(user=self.user,
                                       achievement=Achievement.objects.get(name="Junior forumite"))
        self.client.login(email='galin@email.com', password='Password123')
        data = {
            'title': 'Test Title',
            'content': 'Test Content',
            'forum_categories': self.forum_category.id,
            'media': ''
        }
        response = self.client.post(self.url, data)
        self.assertTrue(Post.objects.filter(title='Test Title', content='Test Content', user=self.user).exists())
