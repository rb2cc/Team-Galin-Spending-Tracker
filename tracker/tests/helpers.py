from tracker.models import Category

class LogInTester:
    """Helper to check if a user is logged in"""
    def _is_logged_in(self):
        return '_auth_user_id' in self.client.session.keys()

class CategoryFunctions:
    """Helper to create some category objects for testing"""
    def _make_categories(self):
        Category.objects.create(name="Food", week_limit=150, is_global=True)
        Category.objects.create(name="Clothes", week_limit=50, is_global=True)
        Category.objects.create(name="Pub", week_limit=50, is_global=False)
