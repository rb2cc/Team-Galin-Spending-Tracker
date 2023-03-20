from django import forms
from django.test import TestCase
from tracker.forms import AddAchievementForm
from tracker.models import Achievement

"""Unit tests for the AddAchievement form"""
class AddAchievementFormTestCase(TestCase):

    def setUp(self):

        self.form_input = {
            'name':'Achievement',
            'description': 'Description',
            'criteria': 'Criteria'
        }

    def test_valid_add_achievement_form(self):
        form = AddAchievementForm(data = self.form_input)
        self.assertTrue(form.is_valid())

    def test_add_achievement_form_has_necessary_fields(self):
        form = AddAchievementForm()
        self.assertIn('name', form.fields)
        self.assertIn('description', form.fields)
        self.assertIn('criteria', form.fields)

    def test_invalid_add_achievement_form(self):
        self.form_input['criteria'] = ''
        form = AddAchievementForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_add_achievement_form_saves_correctly(self):
        form = AddAchievementForm(data = self.form_input)
        before_count = Achievement.objects.count()
        form.save()
        after_count = Achievement.objects.count()
        self.assertEqual(after_count, before_count+1)
        achievement = Achievement.objects.get(name = 'Achievement')
        self.assertEqual(achievement.description, 'Description')
        self.assertEqual(achievement.criteria, 'Criteria')
