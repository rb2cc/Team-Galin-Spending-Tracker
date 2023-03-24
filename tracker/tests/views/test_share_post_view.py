from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from tracker.models import User, Post, Forum_Category, UserLevel, Level
from tracker.views import share_post

class SharePostViewTests(TestCase):

    fixtures = ['tracker/tests/fixtures/default_user.json',
                'tracker/tests/fixtures/forum_fixtures.json']

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.get(email='galin@email.com')
        self.forum_category = Forum_Category.objects.get(title='Test Category')
        self.post = Post.objects.get(title='Test Post')
        self.url = reverse('share_post', kwargs={'id': self.post.id})
        self.post.forum_categories.add(self.forum_category)
        self.level = Level.objects.get(name='level')
        self.userlevel = UserLevel.objects.create(user=self.user, level=self.level, points=20)


    def test_share_post_without_username(self):
        request = self.factory.get(reverse('share_post', args=[str(self.post.id)]))
        request.user = self.user
        response = share_post(request, self.post.id)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.post.title, response.content.decode())

    def test_share_post_with_username(self):
        self.user.username = 'Galinski'
        request = self.factory.get(reverse('share_post', args=[str(self.post.id)]))
        request.user = self.user
        response = share_post(request, self.post.id)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.post.title, response.content.decode())
