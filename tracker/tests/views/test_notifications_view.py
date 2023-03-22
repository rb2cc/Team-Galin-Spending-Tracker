from django.test import TestCase, Client
from django.urls import reverse
from tracker.models import User, Notification

class NotificationsViewTests(TestCase):

    fixtures = ['tracker/tests/fixtures/default_user.json']

    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(email='galin@email.com')
        self.notification = Notification.objects.create(to_user=self.user, created_by=self.user)
        self.url = reverse('notifications')

    def test_view_uses_correct_template(self):
        self.client.login(email='galin@email.com', password='Password123')
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'notifications.html')

    def test_user_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_post_request_with_noti_form(self):
        self.client.login(email='galin@email.com', password='Password123')
        response = self.client.post(self.url, {
            'noti-form': '',
            'noti-id': self.notification.id
        })
        self.assertEqual(response.status_code, 200)
