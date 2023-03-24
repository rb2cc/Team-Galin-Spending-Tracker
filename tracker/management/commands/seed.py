from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.hashers import make_password
import random
from faker import Faker
from tracker.models import Category, User, Expenditure, Achievement, Challenge, Forum_Category, Post, Comment, Reply, UserLevel, Level, Avatar
import datetime
from django.utils.timezone import make_aware
from tinymce.models import HTMLField
from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from hitcount.models import HitCountMixin, HitCount


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

        Avatar.objects.create(user=james,
                        file_name='faker_image_james.png',
                        current_template='faker_image_james.png'
                        )

        john = User.objects.create(
            email = "john@kcl.ac.uk",
            password = password_data,
            first_name = "John",
            last_name = "Smith",
            username=self.faker.text(max_nb_chars=20),
        )
        john.available_categories.add(foodCategoryLocal,travelCategoryLocal, overallCategory)
        
        Avatar.objects.create(user=john,
                        file_name='faker_image_john.png',
                        current_template='faker_image_john.png'
                        )

        sarah = User.objects.create(
            email = "sarah@kcl.ac.uk",
            password = password_data,
            first_name = "Sarah",
            last_name = "Milling",
            username=self.faker.text(max_nb_chars=20),
        )
        sarah.available_categories.add(foodCategoryLocal,travelCategoryLocal, overallCategory)

        Avatar.objects.create(user=sarah,
                        file_name='faker_image_sarah.png',
                        current_template='faker_image_sarah.png'
                        )


        zara = User.objects.create(
            email = "zara@kcl.ac.uk",
            password = password_data,
            first_name = "Zara",
            last_name = "Khan",
            username=self.faker.text(max_nb_chars=20),
        )
        zara.available_categories.add(foodCategoryLocal,travelCategoryLocal, overallCategory)

        Avatar.objects.create(user=zara,
                        file_name='faker_image_zara.png',
                        current_template='faker_image_zara.png'
                        )

        galin = User.objects.create(
            email = "galin@email.com",
            password = password_data,
            first_name = "Galin",
            last_name = "Mihaylov",
            username=self.faker.text(max_nb_chars=20),
        )
        galin.available_categories.add(foodCategoryLocal,travelCategoryLocal, overallCategory)


        kim = User.objects.create(
            email = "kim@kcl.ac.uk",
            password = password_data,
            first_name = "Jungkyu",
            last_name = "Kim",
            username="Ski&SnowGod",
        )
        kim.available_categories.add(foodCategoryLocal,travelCategoryLocal, overallCategory)

        Avatar.objects.create(user=kim,
                        file_name='faker_image_kim.png',
                        current_template='faker_image_kim.png'
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
                    'description': 'Share first post on Facebook, Twitter or Forum',
                    'badge': 'first_share.png'
                },
                {
                    'name': 'Superstar',
                    'description': 'Complete 10 challenges',
                    'badge': 'super_star.png'
                },
                {
                    'name': 'Junior forumite',
                    'description': 'Make your first forum post/reply/comment',
                    'badge': 'forum.png'
                },
                {
                    'name': 'Active contributor',
                    'description': 'Make 10 forum posts/replies/comments',
                    'badge': 'forum.png'
                },
                {
                    'name': 'Forum veteran',
                    'description': 'Make 100 forum posts/replies/comments',
                    'badge': 'forum.png'
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
                },
                {
                    'name': 'Planting pioneer',
                    'description': 'Plant 1 tree in Galin Environmental Project',
                    'badge': 'tree.png'
                },
                {
                    'name': 'Forest friend',
                    'description': 'Plant 10 trees in Galin Environmental Project',
                    'badge': 'tree.png'
                },
                {
                    'name': 'Green guardian',
                    'description': 'Plant 100 trees in Galin Environmental Project',
                    'badge': 'tree.png'
                },
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
            Achievement.objects.create(
                name=achievement['name'],
                description=achievement['description'],
                badge=badge_path
            )

        for challenge in challenges:
            Challenge.objects.create(
                name=challenge['name'],
                description=challenge['description'],
                points=challenge['points'],
                start_date=challenge['start_date'],
                end_date=challenge['end_date']
            )


        rent = Forum_Category.objects.create(title = "Rent",
                                      slug = "1",
                                      description = "Let's talk about rent")
        
        Frugal_Living = Forum_Category.objects.create(title = "Frugal Living",
                                      slug = "3",
                                      description = "Let's talk about how to living more affordably")
        
        money_concerns = Forum_Category.objects.create(title = "Money Concerns",
                                      slug = "4",
                                      description = "Let's talk about your money concerns")
        
        charity = Forum_Category.objects.create(title = "Charity",
                                      slug = "5",
                                      description = "Let's help our local charities!")
        


        # Post 1:

        james_post = Post.objects.create(user=james,
                            title="Cost of living crisis!",
                            slug=str(random.randint(0, 999)),
                            content="What will the government do to help us with the increasing costs!?",
                            date=models.DateTimeField(auto_now_add=True),
                            approved=True,


                            )
        
        comment_james_post = Comment.objects.create(user=john,
                            content="Is the government even functioning properly?",
                            )
        
        reply_james_post = Reply.objects.create(user=john,
                            content="I'm not sure the government is even sure of what they are doing."
                            )

        level = Level.objects.create(name="Levels",
                            description="Creating new levels",
                            required_points=50)


        james_user_level = UserLevel.objects.create(user=james,
                            level=level,
                            points=55
                            )

        john_user_level = UserLevel.objects.create(user=john,
                            level=level,
                            points=55
                            )

        reply_zara = Reply.objects.create(user=zara,
                            content="I'm very upset about this. I thought they would be doing more for us!"
                            )
                            
        zara_user_level = UserLevel.objects.create(user=zara,
                            level=level,
                            points=100
                            )

        james_post.forum_categories.add(rent)
        comment_james_post.replies.add(reply_james_post)
        comment_james_post.replies.add(reply_zara)
        james_post.comments.add(comment_james_post)

                            

        # Post 2:

        zara_post = Post.objects.create(user=zara,
                            title="How we can better serve charities",
                            slug=str(random.randint(0, 999)),
                            content="I want to ask the community, how we think we can better serve our local charities.",
                            date=models.DateTimeField(auto_now_add=True),
                            approved=True,


                            )
        
        comment_zara_post = Comment.objects.create(user=john,
                            content="Are there even any local charities remaining? I only ever see the national ones.",
                            )
        
        comment_zara_post_2 = Comment.objects.create(user=galin,
                            content="I prefer to donate back home. I'm sorry to say this but I think they need my money more.",
                            )
        
        reply_sarah = Reply.objects.create(user=sarah,
                            content="I'm trying to find charities that I really align with so I can feel that my giving is acutally having and impact."
                            )

        reply_james = Reply.objects.create(user=james,
                            content="Which country are you donating to? I would like to donate to international organisations aswell!"
                            )

        sarah_user_level = UserLevel.objects.create(user=sarah,
                            level=level,
                            points=123
                            )
        
        galin_user_level = UserLevel.objects.create(user=galin,
                            level=level,
                            points=53
                            )

        zara_post.forum_categories.add(charity)
        comment_zara_post.replies.add(reply_sarah)
        comment_zara_post_2.replies.add(reply_james)
        zara_post.comments.add(comment_zara_post)
        zara_post.comments.add(comment_zara_post_2)


        # Post 3

        james_post_3 = Post.objects.create(user=james,
                            title=self.faker.text(max_nb_chars=40),
                            slug=str(random.randint(0, 999)),
                            content=self.faker.text(max_nb_chars=200),
                            date=models.DateTimeField(auto_now_add=True),
                            approved=True,


                            )
        
        comment_james_post_3 = Comment.objects.create(user=john,
                            content=self.faker.text(max_nb_chars=200),
                            )
        
        reply_james_post_3 = Reply.objects.create(user=john,
                            content=self.faker.text(max_nb_chars=200)
                            )

        kim_user_level = UserLevel.objects.create(user=kim,
                            level=level,
                            points=55
                            )

        reply_zara_3 = Reply.objects.create(user=zara,
                            content=self.faker.text(max_nb_chars=200)
                            )
                            

        james_post_3.forum_categories.add(rent)
        comment_james_post_3.replies.add(reply_james_post_3)
        comment_james_post_3.replies.add(reply_zara_3)
        james_post_3.comments.add(comment_james_post_3)



        # Post 4:

        kim_post_4 = Post.objects.create(user=kim,
                            title=self.faker.text(max_nb_chars=40),
                            slug=str(random.randint(0, 999)),
                            content=self.faker.text(max_nb_chars=200),
                            date=models.DateTimeField(auto_now_add=True),
                            approved=True,


                            )
        
        comment_kim_post = Comment.objects.create(user=john,
                            content=self.faker.text(max_nb_chars=200),
                            )
        
        comment_kim_post_2 = Comment.objects.create(user=galin,
                            content=self.faker.text(max_nb_chars=300),
                            )
        
        reply_sarah_4 = Reply.objects.create(user=sarah,
                            content=self.faker.text(max_nb_chars=200)
                            )

        reply_james_4 = Reply.objects.create(user=james,
                            content=self.faker.text(max_nb_chars=200)
                            )

        kim_post_4.forum_categories.add(Frugal_Living)
        comment_kim_post.replies.add(reply_sarah_4)
        comment_kim_post_2.replies.add(reply_james_4)
        kim_post_4.comments.add(comment_zara_post)
        kim_post_4.comments.add(comment_zara_post_2)

        
        # Post 5:


        kim_post_5 = Post.objects.create(user=kim,
                            title=self.faker.text(max_nb_chars=40),
                            slug=str(random.randint(0, 999)),
                            content=self.faker.text(max_nb_chars=200),
                            date=models.DateTimeField(auto_now_add=True),
                            approved=True,


                            )
       
        comment_kim_post_3 = Comment.objects.create(user=john,
                            content=self.faker.text(max_nb_chars=200),
                            )
        
        comment_kim_post_4 = Comment.objects.create(user=galin,
                            content=self.faker.text(max_nb_chars=300),
                            )
        
        reply_sarah_5 = Reply.objects.create(user=sarah,
                            content=self.faker.text(max_nb_chars=200)
                            )

        reply_james_5 = Reply.objects.create(user=james,
                            content=self.faker.text(max_nb_chars=200)
                            )
        
        reply_james_5_1 = Reply.objects.create(user=kim,
                            content=self.faker.text(max_nb_chars=200)
                            )
        
        reply_james_5_2 = Reply.objects.create(user=galin,
                            content=self.faker.text(max_nb_chars=200)
                            )


        kim_post_5.forum_categories.add(Frugal_Living)
        comment_kim_post_3.replies.add(reply_sarah_5)
        comment_kim_post_4.replies.add(reply_james_5)
        comment_kim_post_3.replies.add(reply_james_5_1)
        comment_kim_post_3.replies.add(reply_james_5_2)
        kim_post_5.comments.add(comment_kim_post_3)
        kim_post_5.comments.add(comment_kim_post_4)


        # Post 6:
        kim_post_6 = Post.objects.create(user=galin,
                            title=self.faker.text(max_nb_chars=40),
                            slug=str(random.randint(0, 999)),
                            content=self.faker.text(max_nb_chars=200),
                            date=models.DateTimeField(auto_now_add=True),
                            approved=True,


                            )
       
        comment_kim_post_5 = Comment.objects.create(user=sarah,
                            content=self.faker.text(max_nb_chars=200),
                            )
        
        comment_kim_post_6 = Comment.objects.create(user=galin,
                            content=self.faker.text(max_nb_chars=300),
                            )
        comment_kim_post_7 = Comment.objects.create(user=john,
                            content=self.faker.text(max_nb_chars=200),
                            )
        
        comment_kim_post_8 = Comment.objects.create(user=zara,
                            content=self.faker.text(max_nb_chars=300),
                            )
        
        reply_sarah_6 = Reply.objects.create(user=sarah,
                            content=self.faker.text(max_nb_chars=200)
                            )

        reply_james_7 = Reply.objects.create(user=james,
                            content=self.faker.text(max_nb_chars=200)
                            )
        
        reply_james_7_1 = Reply.objects.create(user=james,
                            content=self.faker.text(max_nb_chars=200)
                            )
        
        reply_james_6_1 = Reply.objects.create(user=kim,
                            content=self.faker.text(max_nb_chars=200)
                            )
        
        reply_james_8 = Reply.objects.create(user=galin,
                            content=self.faker.text(max_nb_chars=200)
                            )


        kim_post_6.forum_categories.add(Frugal_Living)
        comment_kim_post_5.replies.add(reply_sarah_6)
        comment_kim_post_6.replies.add(reply_james_7)
        comment_kim_post_7.replies.add(reply_james_7_1)
        comment_kim_post_8.replies.add(reply_james_6_1)
        comment_kim_post_8.replies.add(reply_james_8)
        kim_post_6.comments.add(comment_kim_post_4)
        kim_post_6.comments.add(comment_kim_post_5)
        kim_post_6.comments.add(comment_kim_post_6)
        kim_post_6.comments.add(comment_kim_post_7)

