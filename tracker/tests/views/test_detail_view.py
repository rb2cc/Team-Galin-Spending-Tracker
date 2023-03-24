from django.test import TestCase, Client
from django.urls import reverse
from tracker.models import User, Post, Comment, Reply, UserLevel, Level
from datetime import timedelta
from django.utils import timezone
from tracker.tests.helpers import delete_avatar_after_test

class DetailsViewTests(TestCase):

    fixtures = ['tracker/tests/fixtures/default_user.json']

    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(email='galin@email.com')
        self.otheruser = User.objects.create_user(email='user@email.com', password='Password123')
        self.post = Post.objects.create(user=self.user, title='Test Post', content='Test content', slug='test-slug')
        self.comment = Comment.objects.create(user=self.user, content='Test comment')
        self.reply = Reply.objects.create(user=self.user, content='Test reply')
        self.level = Level.objects.create(name='level', description='description', required_points=100)
        self.userlevel = UserLevel.objects.create(user=self.user, level=self.level, points=1000)
        self.otherlevel = Level.objects.create(name='level', description='description', required_points=10)
        self.otheruserlevel = UserLevel.objects.create(user=self.otheruser, level=self.otherlevel, points=20)
        self.post.comments.add(self.comment)
        self.url = reverse('detail', args=['test-slug'])

    def test_detail_view_status_code(self):
        self.client.login(email='galin@email.com', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_correct_context(self):
        self.client.login(email='galin@email.com', password='Password123')
        response = self.client.get(self.url)
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
        response = self.client.post(self.url, {
            'comment-form': '',
            'comment': 'New test comment',
            'media': ''
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.post.comments.filter(content='New test comment').exists())

    def test_submit_comment_as_other_user(self):
        self.client.login(email='user@email.com', password='Password123')
        response = self.client.post(self.url, {
            'comment-form': '',
            'comment': 'New test comment',
            'media': ''
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.post.comments.filter(content='New test comment').exists())

    def test_submit_reply(self):
        self.client.login(email='galin@email.com', password='Password123')
        response = self.client.post(self.url, {
            'reply-form': '',
            'reply': 'New test reply',
            'media': '',
            'comment-id': self.comment.id
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.post.comments.get(id=self.comment.id).replies.filter(content='New test reply').exists())

    def test_submit_reply_as_other_user(self):
        self.client.login(email='user@email.com', password='Password123')
        response = self.client.post(self.url, {
            'reply-form': '',
            'reply': 'New test reply',
            'media': '',
            'comment-id': self.comment.id
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.post.comments.get(id=self.comment.id).replies.filter(content='New test reply').exists())


    def test_detail_view_uses_correct_template(self):
        self.client.login(email='galin@email.com', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forum/detail.html')

    def test_user_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('home'))

    def test_time_since_older_posts(self):
        test_post = self.post
        timedeltas = [timedelta(minutes=55), timedelta(hours=5), timedelta(days=1),
                      timedelta(weeks=1), timedelta(weeks=5), timedelta(weeks=55)]
        for delta in timedeltas:
            test_post.date = timezone.now() - delta
            test_post.save()
            url = reverse('detail', args=[test_post.slug])
            self.client.login(email='galin@email.com', password='Password123')
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

    def test_post_detail_with_existing_avatar_template(self):
        self.client.login(email='galin@email.com', password='Password123')
        url = reverse('my_avatar')
        response = self.client.get(url, {'random': ''})
        self.assertEqual(response.status_code, 200)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        delete_avatar_after_test(self)

    def test_post_detail_with_deleted_avatar_template(self):
        self.client.login(email='galin@email.com', password='Password123')
        url = reverse('my_avatar')
        response = self.client.get(url, {'random': ''})
        self.assertEqual(response.status_code, 200)
        delete_avatar_after_test(self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_submit_comment_more_than_five_words_long(self):
        self.client.login(email='galin@email.com', password='Password123')
        response = self.client.post(self.url, {
            'comment-form': '',
            'comment': 'x ' * 6,
            'media': ''
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.post.comments.filter(content='x ' * 6).exists())

    def test_submit_comment_with_a_long_word(self):
        self.client.login(email='galin@email.com', password='Password123')
        response = self.client.post(self.url, {
            'comment-form': '',
            'comment': 'x' * 46,
            'media': ''
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.post.comments.filter(content='x' * 46).exists())

    def test_submit_reply_more_than_five_words_long(self):
        self.client.login(email='galin@email.com', password='Password123')
        response = self.client.post(self.url, {
            'reply-form': '',
            'reply': 'x ' * 6,
            'media': '',
            'comment-id': self.comment.id
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.post.comments.get(id=self.comment.id).replies.filter(content='x ' * 6).exists())

    def test_submit_reply_with_a_long_word(self):
        self.client.login(email='galin@email.com', password='Password123')
        response = self.client.post(self.url, {
            'reply-form': '',
            'reply': 'x' * 46,
            'media': '',
            'comment-id': self.comment.id
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.post.comments.get(id=self.comment.id).replies.filter(content='x' * 46).exists())
