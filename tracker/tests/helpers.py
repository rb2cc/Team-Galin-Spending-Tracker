from tracker.models import Category

class LogInTester:

    def _is_logged_in(self):
        return '_auth_user_id' in self.client.session.keys()

class CategoryFunctions:

    def _make_categories(self):
        Category.objects.create(name="Food", week_limit=150, is_global=True)
        Category.objects.create(name="Clothes", week_limit=50, is_global=True)
        Category.objects.create(name="Pub", week_limit=50, is_global=False)
