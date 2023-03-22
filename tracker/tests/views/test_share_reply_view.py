from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from tracker.models import User, Post, Comment, Reply, Forum_Category, UserLevel, Level
from tracker.views import share_reply

class ShareReplyViewTests(TestCase):

    fixtures = ['tracker/tests/fixtures/default_user.json']

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.get(email='galin@email.com')
        self.forum_category = Forum_Category.objects.create(title='Test Category', slug='test-category', description='Description')
        self.post = Post.objects.create(user=self.user, title='Test Post', content='Test content')
        self.comment = Comment.objects.create(user=self.user, content='Test commet content')
        self.reply = Reply.objects.create(user=self.user, content='Test reply content')
        self.post.forum_categories.add(self.forum_category)
        self.post.comments.add(self.comment)
        self.comment.replies.add(self.reply)
        self.url = reverse('share_reply', kwargs={'id': self.reply.id})
        self.level = Level.objects.create(name='level', description='description', required_points=10)
        self.userlevel = UserLevel.objects.create(user=self.user, level=self.level, points=20)


    def test_share_reply_without_username(self):
        request = self.factory.get(reverse('share_reply', args=[str(self.reply.id)]))
        request.user = self.user
        response = share_reply(request, self.reply.id)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.reply.content, response.content.decode())

    def test_share_reply_with_username(self):
        self.user.username = 'Galinski'
        request = self.factory.get(reverse('share_reply', args=[str(self.reply.id)]))
        request.user = self.user
        response = share_reply(request, self.reply.id)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.reply.content, response.content.decode())
