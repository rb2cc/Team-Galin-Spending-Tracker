from django.db import migrations

def create_achievements(apps, schema_editor):
    Achievement = apps.get_model('tracker', 'Achievement')

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
        }
    ]

    for achievement in achievements:
        badge_path = "badges/" + achievement['badge']
        achievement_obj = Achievement.objects.create(
            name=achievement['name'],
            description=achievement['description'],
            badge=badge_path
        )

class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_achievements),
    ]

