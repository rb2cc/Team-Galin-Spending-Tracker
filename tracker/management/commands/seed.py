from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.hashers import make_password
import random
from faker import Faker
from tracker.models import Category, User, Expenditure
import datetime
from django.utils.timezone import make_aware


class Command(BaseCommand):
    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):

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

        james = User.objects.create(
            email = "james@kcl.ac.uk",
            password = password_data,
            first_name = "Yusheng",
            last_name = "Lu",
        )
        james.available_categories.add(foodCategoryLocal,travelCategoryLocal)

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