from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.hashers import make_password
import random
from faker import Faker
from tracker.models import Category, User, Expenditure, Achievement, Challenge
import datetime
from django.utils.timezone import make_aware


class Command(BaseCommand):
    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):

        User.objects.create_superuser(email = "admin@email.com", password = "Password123") # creating admin account

        password_data = make_password('Password123')

        foodCategory = Category.objects.create(
            name = "food",
            week_limit = 500,
            is_global = True
        )

        travelCategory = Category.objects.create(
            name = "travel",
            week_limit = 100,
            is_global = True
        )

        foodCategoryLocal = Category.objects.create(
            name = "food",
            week_limit = 500,
            is_global = False
        )

        travelCategoryLocal = Category.objects.create(
            name = "travel",
            week_limit = 100,
            is_global = False
        )

        overallCategory = Category.objects.create(
            name = "Overall",
            week_limit = 600,
            is_overall = True
        )

        james = User.objects.create(
            email = "james@kcl.ac.uk",
            password = password_data,
            first_name = "Yusheng",
            last_name = "Lu",
        )
        james.available_categories.add(foodCategoryLocal,travelCategoryLocal, overallCategory)

        galin = User.objects.create(
            email = "galin@email.com",
            password = password_data,
            first_name = "Galin",
            last_name = "Mihaylov",
        )

        for _ in range(0,100):
            Expenditure.objects.create(
                category = foodCategoryLocal,
                title = self.faker.text(max_nb_chars=20),
                description = self.faker.text(max_nb_chars=200),
                expense = random.randint(0,10000)/100,
                date_created = make_aware(self.faker.date_time_between(start_date = "-1y", end_date = "now")),
                user = james,
            )

        for _ in range(0,100):
            Expenditure.objects.create(
                category = travelCategoryLocal,
                title = self.faker.text(max_nb_chars=20),
                description = self.faker.text(max_nb_chars=200),
                expense = random.randint(0,10000)/100,
                date_created = make_aware(self.faker.date_time_between(start_date = "-1y", end_date = "now")),
                user = james,
            )

        achievements = [
                {
                    'name': 'Budget boss',
                    'description': 'Create first custom category',
                    'badge': 'budget_boss.png'
                },
                {
                    'name': 'Wise spender',
                    'description': 'Complete first challenge',
                    'badge': 'wise_spender.png'
                },
                {
                    'name': 'First share',
                    'description': 'Share first post on Facebook or Twitter',
                    'badge': 'first_share.png'
                },
                {
                    'name': 'Superstar',
                    'description': 'Complete 10 challenges',
                    'badge': 'super_star.png'
                },
                {
                    'name': 'First forum post',
                    'description': 'Make your first forum post',
                    'badge': 'first_forum.png'
                },
                {
                    'name': 'New user',
                    'description': 'Create an account on the platform',
                    'badge': 'new_user.png'
                },
                {
                    'name': 'First expenditure',
                    'description': 'Create first custom expenditure',
                    'badge': 'first_expenditure.png'
                },
                {
                    'name': 'Avatar master',
                    'description': 'Create an avatar',
                    'badge': 'avatar_master.png'
                }
            ]

        challenges = [
            {
                'name': 'Track your spending',
                'description': 'Track all of your expenses for a week',
                'points': 50,
                'start_date': datetime.date(2023, 2, 1),
                'end_date': datetime.date(2023, 2, 7)
            },
            {
                'name': 'Cut out subscriptions',
                'description': 'Cancel all of your subscription services for a month',
                'points': 100,
                'start_date': datetime.date(2023, 3, 1),
                'end_date': datetime.date(2023, 3, 31)
            },
            {
                'name': 'Eat in',
                'description': 'Cook all of your meals at home for a week',
                'points': 50,
                'start_date': datetime.date(2023, 4, 1),
                'end_date': datetime.date(2023, 4, 7)
            },
            {
                'name': 'Budget better',
                'description': 'Create a budget and stick to it for a month',
                'points': 100,
                'start_date': datetime.date(2023, 5, 1),
                'end_date': datetime.date(2023, 5, 31)
            },
            {
                'name': 'No impulse buys',
                'description': 'Don\'t make any impulse purchases for a week',
                'points': 50,
                'start_date': datetime.date(2023, 6, 1),
                'end_date': datetime.date(2023, 6, 7)
            },
            {
                'name': 'Save on groceries',
                'description': 'Cut your grocery bill by 20% for a month',
                'points': 100,
                'start_date': datetime.date(2023, 7, 1),
                'end_date': datetime.date(2023, 7, 31)
            },
            {
                'name': 'No takeout',
                'description': 'Don\'t eat out or order takeout for a week',
                'points': 50,
                'start_date': datetime.date(2023, 8, 1),
                'end_date': datetime.date(2023, 8, 7)
            },
            {
                'name': 'Shop smarter',
                'description': 'Find a good deal on something you need and save money',
                'points': 100,
                'start_date': datetime.date(2023, 9, 1),
                'end_date': datetime.date(2023, 9, 30)
            },
            {
                'name': 'Sell unused items',
                'description': 'Sell any unused items you have and make extra money',
                'points': 50,
                'start_date': datetime.date(2023, 10, 1),
                'end_date': datetime.date(2023, 10, 7)
            },
            {
                'name': 'DIY project',
                'description': 'Take on a DIY project instead of buying something new',
                'points': 100,
                'start_date': datetime.date(2023, 11, 1),
                'end_date': datetime.date(2023, 11, 30)
            },
        ]

        for achievement in achievements:
            badge_path = "badges/" + achievement['badge']
            achievement_obj = Achievement.objects.create(
                name=achievement['name'],
                description=achievement['description'],
                badge=badge_path
            )

        for challenge in challenges:
            challenge_obj = Challenge.objects.create(
                name=challenge['name'],
                description=challenge['description'],
                points=challenge['points'],
                start_date=challenge['start_date'],
                end_date=challenge['end_date']
            )
