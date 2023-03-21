from django import forms
from django.test import TestCase
from tracker.forms import AddChallengeForm
from tracker.models import Challenge
import datetime

"""Unit tests for the AddChallenge form"""
class AddChallengeFormTestCase(TestCase):

    def setUp(self):

        self.form_input = {
            'name':'Challenge',
            'description': 'Description',
            'points': 10,
            'start_date': datetime.date(2023, 3, 3),
            'end_date': datetime.date(2023, 3, 4)
        }

    def test_valid_add_challenge_form(self):
        form = AddChallengeForm(data = self.form_input)
        self.assertTrue(form.is_valid())

    def test_add_challenge_form_has_necessary_fields(self):
        form = AddChallengeForm()
        self.assertIn('name', form.fields)
        self.assertIn('description', form.fields)
        self.assertIn('points', form.fields)
        self.assertIn('start_date', form.fields)
        self.assertIn('end_date', form.fields)

    def test_invalid_add_challenge_form(self):
        self.form_input['points'] = 'abc'
        form = AddChallengeForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_add_challenge_form_saves_correctly(self):
        form = AddChallengeForm(data = self.form_input)
        before_count = Challenge.objects.count()
        form.save()
        after_count = Challenge.objects.count()
        self.assertEqual(after_count, before_count+1)
        challenge = Challenge.objects.get(name = 'Challenge')
        self.assertEqual(challenge.description, 'Description')
        self.assertEqual(challenge.points, 10)
        self.assertEqual(challenge.start_date, datetime.date(2023, 3, 3))
        self.assertEqual(challenge.end_date, datetime.date(2023, 3, 4))
