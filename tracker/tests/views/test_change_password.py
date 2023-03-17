from django.test import TestCase
from django.urls import reverse
from tracker.models import User, Activity

class ChangePasswordSuccessViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpassword'
        )
        self.url = reverse('change_password_success')
        self.client.login(email='testuser@example.com', password='testpassword')

    def test_change_password_success_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'change_password_success.html')
        self.assertEqual(Activity.objects.filter(user=self.user, name="You've changed your password").count(), 1)