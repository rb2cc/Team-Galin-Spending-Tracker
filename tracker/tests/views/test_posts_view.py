from django.test import TestCase, Client
from django.urls import reverse
from django.core.paginator import Paginator
from tracker.models import User, Post, Forum_Category, Comment
from tracker.views import posts

class PostsViewTests(TestCase):

    fixtures = ['tracker/tests/fixtures/default_user.json']

    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(email='galin@email.com')
        self.forum_category = Forum_Category.objects.create(title='Test Category', slug='test-category', description='Description')
        self.url = reverse('posts')
        self.post1 = Post.objects.create(user=self.user, title='Test Post 1', content='Test content 1')
        self.post1.forum_categories.add(self.forum_category)
        self.post2 = Post.objects.create(user=self.user, title='Test Post 2', content='Test content 2')
        self.post2.forum_categories.add(self.forum_category)

    def test_posts_url(self):
        self.assertEqual(self.url, '/posts/')

    def test_posts_view_uses_correct_template(self):
        self.client.login(email='galin@email.com', password='Password123')
        response = self.client.get(f'/posts/{self.forum_category.slug}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forum/posts.html')

    def test_posts_view_no_page_number(self):
        self.client.login(email='galin@email.com', password='Password123')
        response = self.client.get(f'/posts/{self.forum_category.slug}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['posts']), 2)

    def test_correct_context(self):
        self.client.login(email='galin@email.com', password='Password123')
        response = self.client.get(f'/posts/{self.forum_category.slug}/')
        self.assertIn('posts', response.context)
        self.assertIn('forum', response.context)
        self.assertIn('title', response.context)

    def test_posts_view_invalid_page_number(self):
        self.client.login(email='galin@email.com', password='Password123')
        response = self.client.get(f'/posts/{self.forum_category.slug}/', {'page': 100})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['posts']), 2)

    def test_posts_view_page_not_an_integer(self):
        self.client.login(email='galin@email.com', password='Password123')
        response = self.client.get(f'/posts/{self.forum_category.slug}/', {'page': 'not-an-integer'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['posts']), 2)

    def test_posts_view_category_not_found(self):
        self.client.login(email='galin@email.com', password='Password123')
        response = self.client.get('/posts/non-existent-category/')
        self.assertEqual(response.status_code, 404)
