from django.test import TestCase, Client
from django.urls import reverse
from tracker.models import User, Post, Comment, Reply, Forum_Category


class DeletePostViewTests(TestCase):

    fixtures = ['tracker/tests/fixtures/default_user.json',
                'tracker/tests/fixtures/forum_fixtures.json']

    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(email='galin@email.com')
        self.forum_category = Forum_Category.objects.get(title='Test Category')
        self.post = Post.objects.create(user=self.user, title='Test Post', content='Test content')
        self.comment = Comment.objects.create(user=self.user, content='Test commet content')
        self.reply = Reply.objects.create(user=self.user, content='Test reply content')
        self.post.forum_categories.add(self.forum_category)
        self.post.comments.add(self.comment)
        self.comment.replies.add(self.reply)
        self.url = reverse('delete_post', kwargs={'id': self.post.id})

    def test_user_can_delete_own_post(self):
        self.client.login(email='galin@email.com', password='Password123')
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('forum_home'))
        self.assertFalse(Post.objects.filter(id=self.post.id).exists())

    def test_deleting_post_also_deletes_comments_and_replies(self):
        self.client.login(email='galin@email.com', password='Password123')
        response = self.client.get(self.url)
        self.assertFalse(Comment.objects.filter(id=self.comment.id).exists())
        self.assertFalse(Reply.objects.filter(id=self.reply.id).exists())

    def test_attempting_to_delete_non_existent_post(self):
        self.client.login(email='galin@email.com', password='Password123')
        non_existent_post_url = reverse('delete_post', kwargs={'id': self.post.id + 1})
        response = self.client.get(non_existent_post_url)
        self.assertRedirects(response, reverse('forum_home'))
