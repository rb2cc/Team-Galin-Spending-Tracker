from django.test import RequestFactory, TestCase, Client
from tracker.views import save_item_position
from django.http import JsonResponse
from django.urls import reverse
from tracker.models import User, Level, UserLevel, Tree
import json

class SaveItemPositionViewTestCase(TestCase):

    fixtures = ['tracker/tests/fixtures/default_user.json']

    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(email='test@example.com')
        self.tree = Tree.objects.create(user=self.user, x_position=500, y_position=50)
        self.factory = RequestFactory()

    def test_save_item_position_view(self):
        self.client.force_login(self.user)
        data = {
            "x": 100,
            "y": 100,
            "tree_id": self.tree.tree_id,
        }
        request = self.factory.post('/save-item-position/', data=json.dumps(data),
                                    content_type='application/json')
        request.user = self.user
        csrf_token = 'test_csrf_token_value'
        request.META['HTTP_X_CSRFTOKEN'] = csrf_token
        response = save_item_position(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, JsonResponse({'success': True}).content)
        self.tree.refresh_from_db()
        self.assertEqual(self.tree.x_position, 100)
        self.assertEqual(self.tree.y_position, 100)