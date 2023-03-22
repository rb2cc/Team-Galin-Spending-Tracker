from django.test import TestCase, Client
from django.urls import reverse
from tracker.models import User, Post, Comment, Reply, Forum_Category, UserLevel, Level


class EditPostViewTests(TestCase):

    fixtures = ['tracker/tests/fixtures/default_user.json']

    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(email='galin@email.com')
        self.forum_category = Forum_Category.objects.create(title='Test Category', slug='test-category', description='Description')
        self.post = Post.objects.create(user=self.user, title='Test Post', content='Test content')
        self.comment = Comment.objects.create(user=self.user, content='Test commet content')
        self.reply = Reply.objects.create(user=self.user, content='Test reply content')
        self.post.forum_categories.add(self.forum_category)
        self.post.comments.add(self.comment)
        self.comment.replies.add(self.reply)
        self.level = Level.objects.create(name='level', description='description', required_points=10)
        self.userlevel = UserLevel.objects.create(user=self.user, level=self.level, points=20)
        self.url = reverse('edit_post', kwargs={'id': self.post.id})

    def test_edit_post_url(self):
        self.assertEqual(self.url, '/edit_post/1')

    def test_correct_context(self):
        self.client.login(email='galin@email.com', password='Password123')
        response = self.client.get(self.url)
        self.assertIn('form', response.context)

    def test_edit_post_view_uses_correct_template(self):
        self.client.login(email='galin@email.com', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forum/edit_post.html')

    def test_post_request_with_valid_data_updates_post(self):
        self.client.login(email='galin@email.com', password='Password123')
        data = {
            'title': 'Edited Title',
            'content': 'Edited Content',
            'forum_categories': self.forum_category.id,
            'media': ''
        }
        response = self.client.post(self.url, data)
        self.assertRedirects(response, Post.objects.get(title='Edited Title', user=self.user).get_url())
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Edited Title')
        self.assertEqual(self.post.content, 'Edited Content')

    def test_post_request_with_invalid_data_does_not_update_post(self):
        self.client.login(email='galin@email.com', password='Password123')
        data = {
            'title': '',
            'content': '',
            'forum_categories': self.forum_category.id,
            'media': ''
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Test Post')
        self.assertEqual(self.post.content, 'Test content')

    def test_post_does_not_exist(self):
        self.client.login(email='galin@email.com', password='Password123')
        non_existent_post_url = reverse('edit_post', kwargs={'id': self.post.id + 1})
        response = self.client.post(non_existent_post_url)
        self.assertRedirects(response, reverse('forum_home'))
