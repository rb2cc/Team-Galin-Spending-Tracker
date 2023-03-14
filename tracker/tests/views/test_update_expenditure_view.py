from django.test import TestCase
from django.urls import reverse
from tracker.models import User, Category, Expenditure
from tracker.forms import ExpenditureForm

class UpdateExpenditureViewTestCase(TestCase):
    fixtures = ['tracker/tests/fixtures/default_user.json',
                'tracker/tests/fixtures/default_category.json',
                'tracker/tests/fixtures/extra_categories.json']
    
    def setUp(self):
        url = 'test_image/fortlobby.png'
        self.user = User.objects.get(email = 'james@example.org')
        self.cat_one = Category.objects.get(name = 'Test')
        self.cat_two = Category.objects.get(name = 'Test2')
        self.overall_cat = Category.objects.get(name = 'Test4')
        self.url = reverse('update_expenditure', kwargs={'id': 0})
        self.expenditure = Expenditure.objects.create(
            category = self.cat_one,
            title = 'Test payment',
            description = 'Paying fellas',
            expense = 15,
            image = url,
            user = self.user
        )
        self.form_input_two = {
            'title':'Change payment',
            'expense': 150,
            'description': 'Paying other fellas',
            'category': self.cat_two,
            'image': url
        }

    def test_update_expenditure_url(self):
        self.assertEqual(self.url, '/update_expenditure/0')

    def test_post_update_expenditure(self):
        self.user.available_categories.add(self.cat_one, self.cat_two, self.overall_cat)
        self.client.login(username = self.user.email, password = 'Lu123')
        before_count = Expenditure.objects.count()
        response = self.client.post(self.url, self.form_input_two, follow = True)
        after_count = Expenditure.objects.count()
        self.assertEqual(after_count, before_count)
        # remaining = list(map(lambda expenditure: expenditure.title, list(Expenditure.objects.all())))
        # self.assertFalse('Test payment' in remaining)
        # self.assertTrue('Change payment' in remaining)
        self.assertRedirects(response, reverse('expenditure_list'), status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'expenditure_list.html')

    def test_get_update_expenditure(self):
        self.user.available_categories.add(self.cat_one, self.cat_two)
        self.client.login(username = self.user.email, password = 'Lu123')
        response = self.client.get(self.url)
        form = response.context['form']
        self.assertEqual(form.instance, self.expenditure)
        self.assertTrue(isinstance(form, ExpenditureForm))
        self.assertTemplateUsed(response, 'update_expenditure.html')