from django.test import TestCase, Client
from django.urls import reverse
from tracker.models import User, Post, Comment, Reply, Forum_Category, UserLevel, Level


class DeleteReplyViewTests(TestCase):

    fixtures = ['tracker/tests/fixtures/default_user.json',
                'tracker/tests/fixtures/forum_fixtures.json']

    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(email='galin@email.com')
        self.forum_category = Forum_Category.objects.get(title='Test Category')
        self.post = Post.objects.get(title='Test Post')
        self.comment = Comment.objects.create(user=self.user, content='Test commet content')
        self.reply = Reply.objects.create(user=self.user, content='Test reply content')
        self.post.forum_categories.add(self.forum_category)
        self.post.comments.add(self.comment)
        self.comment.replies.add(self.reply)
        self.level = Level.objects.create(name='level', description='description', required_points=10)
        self.userlevel = UserLevel.objects.create(user=self.user, level=self.level, points=20)
        self.url = reverse('delete_reply', kwargs={'id': self.reply.id})

    def test_user_can_delete_own_reply(self):
        self.client.login(email='galin@email.com', password='Password123')
        response = self.client.get(self.url)
        self.assertRedirects(response, self.post.get_url())
        self.assertFalse(Reply.objects.filter(id=self.reply.id).exists())\

    def test_attempting_to_delete_non_existent_reply(self):
        self.client.login(email='galin@email.com', password='Password123')
        non_existent_reply_url = reverse('delete_reply', kwargs={'id': self.reply.id + 1})
        response = self.client.get(non_existent_reply_url)
        self.assertRedirects(response, reverse('forum_home'))
