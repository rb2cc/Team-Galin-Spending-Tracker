from django.test import TransactionTestCase, Client
from django.urls import reverse
from tracker.models import User, Post, Comment, Reply, Forum_Category, UserLevel, Level, Achievement, UserAchievement


class HandleShareViewTests(TransactionTestCase):

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
        self.url = reverse('handle_share')
        self.first_share_achievement = Achievement.objects.create(name="First share")

    def test_handle_share_url(self):
        self.assertEqual(self.url, '/handle_share/')

    def test_view_creates_new_user_activity_when_sharing(self):
        self.client.login(email='galin@email.com', password='Password123')
        response = self.client.get(self.url, {'type': 'Image', 'name': 'Name', 'site': 'Instagram', 'share_url': 'www.instagram.com'})
        self.assertEqual(response.url, 'www.instagram.com')

    def test_view_does_not_raise_error(self):
        self.client.login(email='galin@email.com', password='Password123')
        UserAchievement.objects.create(user=self.user, achievement=self.first_share_achievement)
        response = self.client.get(self.url, {'type': 'Image', 'name': 'Name', 'site': 'Instagram', 'share_url': 'www.instagram.com'})
        user_achievement = UserAchievement.objects.filter(user=self.user, achievement=self.first_share_achievement)
        self.assertEqual(user_achievement.count(), 1)

    def test_view_object_does_not_exist(self):
        self.first_share_achievement.delete()
        self.client.login(email='galin@email.com', password='Password123')
        response = self.client.get(self.url, {'type': 'Image', 'name': 'Name', 'site': 'Instagram', 'share_url': 'www.instagram.com'})
        self.assertEqual(response.url, 'www.instagram.com')
