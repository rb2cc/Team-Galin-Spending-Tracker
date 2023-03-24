from django.test import TestCase, Client
from django.urls import reverse
from tracker.models import User, Category, Expenditure
from tracker import expenditure_views


class ExpenditureViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpassword',
            first_name='Test',
            last_name='User'
        )
        self.category = Category.objects.create(
            name='TestCategory',
            week_limit=100,
        )
        self.expenditure = Expenditure.objects.create(
            category=self.category,
            title='Test Expenditure',
            description='This is a test expenditure',
            expense=50,
            user=self.user
        )
        self.user.available_categories.add(self.category)

    def test_expenditure_list_view(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('expenditure_list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.expenditure, response.context['spendings'])
        self.assertIn(self.category, response.context['categories'])

    def test_bin_expenditure_view(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('bin_expenditure'), {'radio_pk': self.expenditure.pk})
        self.assertEqual(response.status_code, 302)
        self.expenditure.refresh_from_db()
        self.assertTrue(self.expenditure.is_binned)

    def test_recover_expenditure_view(self):
        self.client.force_login(self.user)
        self.expenditure.is_binned = True
        self.expenditure.save()
        response = self.client.post(reverse('recover_expenditure'), {'radio_pk': self.expenditure.pk})
        self.assertEqual(response.status_code, 302)
        self.expenditure.refresh_from_db()
        self.assertFalse(self.expenditure.is_binned)

    def test_delete_expenditure_view(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('delete_expenditure'), {'radio_pk': self.expenditure.pk})
        self.assertEqual(response.status_code, 302)
        with self.assertRaises(Expenditure.DoesNotExist):
            self.expenditure.refresh_from_db()

    def test_update_expenditure_view(self):
        self.client.force_login(self.user)
        updated_data = {
            'title': 'Updated Expenditure',
            'description': 'This is an updated test expenditure',
            'expense': 100,
            'category': self.category.pk
        }
        response = self.client.post(reverse('update_expenditure', kwargs={'id': self.expenditure.pk}), updated_data)
        self.assertEqual(response.status_code, 302)
        self.expenditure.refresh_from_db()
        self.assertEqual(self.expenditure.title, updated_data['title'])
        self.assertEqual(self.expenditure.description, updated_data['description'])
        self.assertEqual(self.expenditure.expense, updated_data['expense'])

    def test_filter_by_title_view(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('filter_title'), {'q': 'Test Expenditure'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.expenditure, response.context['spendings'])

    def test_filter_by_category_view(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('filter_category'), {'q': self.category.pk})
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.expenditure, response.context['spendings'])

    def test_filter_by_miscellaneous_view(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('filter_miscellaneous'), {'q': 'desc'})
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('filter_miscellaneous'), {'q': 'asc'})
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('filter_miscellaneous'), {'q': 'old'})
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('filter_miscellaneous'), {'q': 'new'})
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('filter_miscellaneous'), {'q': 'wrong filter'})
        self.assertEqual(response.status_code, 200)

    def test_binned_expenditure_list_view(self):
        self.client.force_login(self.user)
        self.expenditure.is_binned = True
        self.expenditure.save()
        response = self.client.get(reverse('expenditure_bin'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.expenditure, response.context['binned_spendings'])
        self.assertIn(self.category, response.context['categories'])

    def test_bin_expenditure_view_with_invalid_pk(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('bin_expenditure'), {'radio_pk': -1})
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.expenditure.is_binned)

    def test_recover_expenditure_view_with_invalid_pk(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('recover_expenditure'), {'radio_pk': -1})
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.expenditure.is_binned)

    def test_delete_expenditure_view_with_invalid_pk(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('delete_expenditure'), {'radio_pk': -1})
        self.assertEqual(response.status_code, 302)
        self.expenditure.refresh_from_db()
        self.assertIsNotNone(self.expenditure)

    def test_update_expenditure_view_no_form_submission(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('update_expenditure', kwargs={'id': self.expenditure.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.category, response.context['categories'])

    def test_filter_by_title_view_no_query(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('filter_title'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.expenditure, response.context['spendings'])

    def test_filter_by_category_view_no_query(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('filter_category'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.expenditure, response.context['spendings'])

    def test_update_expenditure_view_with_changed_category(self):
        self.client.force_login(self.user)
        new_category = Category.objects.create(name='NewTestCategory', week_limit=200)
        self.user.available_categories.add(new_category)
        updated_data = {
            'title': 'Updated Expenditure',
            'description': 'This is an updated test expenditure',
            'expense': 100,
            'category': new_category.pk
        }
        response = self.client.post(reverse('update_expenditure', kwargs={'id': self.expenditure.pk}), updated_data)
        self.assertEqual(response.status_code, 302)
        self.expenditure.refresh_from_db()
        self.assertEqual(self.expenditure.category, new_category)

    def test_bin_expenditure_view_without_radio_pk(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('bin_expenditure'))
        self.assertEqual(response.status_code, 302)
        self.expenditure.refresh_from_db()
        self.assertFalse(self.expenditure.is_binned)

    def test_recover_expenditure_view_without_radio_pk(self):
        self.client.force_login(self.user)
        self.expenditure.is_binned = True
        self.expenditure.save()
        response = self.client.post(reverse('recover_expenditure'))
        self.assertEqual(response.status_code, 302)
        self.expenditure.refresh_from_db()
        self.assertTrue(self.expenditure.is_binned)

    def test_delete_expenditure_view_without_radio_pk(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('delete_expenditure'))
        self.assertEqual(response.status_code, 302)
        self.expenditure.refresh_from_db()
        self.assertIsNotNone(self.expenditure)

    def test_bin_expenditure_get_request(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('bin_expenditure'))
        self.assertEqual(response.status_code, 302)

    def test_recover_expenditure_get_request(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('recover_expenditure'))
        self.assertEqual(response.status_code, 302)

    def test_delete_expenditure_get_request(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('delete_expenditure'))
        self.assertEqual(response.status_code, 302)

    def test_update_expenditure_post_request_invalid_form(self):
        self.client.force_login(self.user)
        updated_data = {
            'title': 'Updated Expenditure',
            'description': 'This is an updated test expenditure',
            'expense': -150,
            'category': self.category.pk
        }
        response = self.client.post(reverse('update_expenditure', kwargs={'id': self.expenditure.pk}), updated_data)
        self.assertEqual(response.status_code, 200)

    def test_update_expenditure_with_no_changes(self):
        self.client.force_login(self.user)
        updated_data = {
            'title': self.expenditure.title,
            'description': self.expenditure.description,
            'expense': self.expenditure.expense,
            'category': self.category.pk
        }
        response = self.client.post(reverse('update_expenditure', kwargs={'id': self.expenditure.pk}), updated_data)
        self.assertEqual(response.status_code, 302)

    def test_bin_overflow_deletes_expenditures(self):
        self.client.force_login(self.user)
        for id in range (2, 13):
            test_expenditure= self.expenditure
            test_expenditure.id = id
            test_expenditure.save()
            response = self.client.post(reverse('bin_expenditure'), {'radio_pk': id})
            self.assertEqual(response.status_code, 302)
