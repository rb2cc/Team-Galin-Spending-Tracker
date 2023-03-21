from django.test import TestCase, Client
from django.urls import reverse
from tracker.models import User, Post, Comment, Reply, UserLevel, Level

class DetailsViewTests(TestCase):

    fixtures = ['tracker/tests/fixtures/default_user.json']

    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(email='galin@email.com')
        self.post = Post.objects.create(user=self.user, title='Test Post', content='Test content', slug='test-slug')
        self.comment = Comment.objects.create(user=self.user, content='Test comment')
        self.reply = Reply.objects.create(user=self.user, content='Test reply')
        self.level = Level.objects.create(name='level', description='description', required_points=10)
        self.userlevel = UserLevel.objects.create(user=self.user, level=self.level, points=20)
        self.post.comments.add(self.comment)
        self.detail_url = reverse('detail', args=['test-slug'])

    def test_detail_view_status_code(self):
        self.client.login(email='galin@email.com', password='Password123')
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)

    def test_correct_context(self):
        self.client.login(email='galin@email.com', password='Password123')
        response = self.client.get(self.detail_url)
        self.assertIn('post', response.context)
        self.assertIn('title', response.context)
        self.assertIn('points', response.context)
        self.assertIn('avatars', response.context)
        self.assertIn('tier_colours', response.context)
        self.assertIn('user_levels', response.context)
        self.assertIn('user_tier_names', response.context)
        self.assertIn('posts', response.context)

    def test_submit_comment(self):
        self.client.login(email='galin@email.com', password='Password123')
        response = self.client.post(self.detail_url, {
            'comment-form': '',
            'comment': 'New test comment',
            'media': ''
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.post.comments.filter(content='New test comment').exists())

    # def test_submit_reply(self):
    #     self.client.login(email='galin@email.com', password='Password123')
    #     response = self.client.post(self.detail_url, {
    #         'reply-form': '',
    #         'reply': 'New test reply',
    #         'media': '',
    #         'comment_id':
    #     })
        # self.assertEqual(response.status_code, 200)
        # self.assertTrue(self.post.comments.filter(content='New test comment').exists())

    def test_detail_view_uses_correct_template(self):
        self.client.login(email='galin@email.com', password='Password123')
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forum/detail.html')
