from django.db import migrations
import datetime

def create_objects(apps, schema_editor):
    Achievement = apps.get_model('tracker', 'Achievement')
    Challenge = apps.get_model('tracker', 'Challenge')

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

class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_objects),
    ]

