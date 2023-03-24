from .forms import SignUpForm, LogInForm, EditUserForm, ReportForm, PostForm, CreateUserForm
from .models import User, Category, Expenditure, Challenge, UserChallenge, Achievement, UserAchievement, Level, UserLevel, Activity, Post, Forum_Category, Comment, Reply, Avatar, Notification
from .forms import SignUpForm, LogInForm, ExpenditureForm, AddCategoryForm, AddChallengeForm, AddAchievementForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import user_passes_test, login_required
from django.urls import reverse, reverse_lazy
from django.views import generic
from datetime import date, timedelta
from django.utils import timezone
from django.db import IntegrityError
from math import floor
from urllib.parse import urlencode, unquote
import math
import os
from django.conf import settings
import re
from django.template.defaulttags import register
from django.views.decorators.cache import cache_control
from django.http import HttpResponse, QueryDict
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.exceptions import ObjectDoesNotExist
from .utils import update_views
import hashlib
import random
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Tree
import json
from .utils import create_notification, create_achievement_notification
from .send_emails import Emailer
from .helpers import login_prohibited, user_prohibited, anonymous_prohibited, anonymous_prohibited_with_id
from dateutil.relativedelta import relativedelta, MO, SU

# Create your views here.

#view function that will validate login form data and redirect to the relevant homepage
#depending if theyre an admin or standard user
@login_prohibited
def home(request):
    if request.method == 'POST':
        form = LogInForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(email=email, password=password)
            if user is not None:
                login(request, user)
                if user.is_superuser or user.is_staff == True:
                    return redirect('admin_dashboard')
                else:
                    return redirect('landing_page')
        messages.add_message(request, messages.ERROR, "The credentials provided were invalid")
    form = LogInForm()
    return render(request, 'home.html', {'form': form})

#view function that will create a new user object from the form data in the request
#creates and gives achievements to the new user for signing up as well
@login_prohibited
def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            if not User.objects.filter(email=form.cleaned_data.get('email')).exists():
                user = form.save()
                global_categories = Category.objects.filter(is_global=True)
                overall_count = 0
                for x in global_categories:
                    tempName = x.name
                    tempLimit = x.week_limit
                    overall_count += x.week_limit
                    tempCategory = Category.objects.create(name=tempName, week_limit=tempLimit)
                    user.available_categories.add(tempCategory)
                login(request, user)
                try:
                    UserAchievement.objects.create(user=request.user, achievement = Achievement.objects.get(name="New user"))
                except ObjectDoesNotExist:
                    pass
                sign_up_achievement_1 = Activity.objects.create(user=request.user, image = "images/user.png", name = "You've created an account on Galin's Spending Tracker")
                sign_up_achievement_2 = Activity.objects.create(user=request.user, image = "badges/new_user.png", name = "You've earned \"New user\" achievement")
                overall = Category.objects.create(name="Overall", week_limit=overall_count, is_overall = True)
                user.available_categories.add(overall)
                create_achievement_notification(request, request.user, "achievement", sign_up_achievement_1.name)
                create_achievement_notification(request, request.user, "achievement", sign_up_achievement_2.name)
                Emailer.send_register_email("Account Registration", request.user.email, request.user.first_name)
                return redirect('landing_page')
            else:
                messages.add_message(request, messages.ERROR, "This email has already been registered")
    else:
        form = SignUpForm()
    return render(request, 'sign_up.html', {'form': form})

# logs out user
def log_out(request):
    logout(request)
    return redirect('home')

# returns the user is not logged in
def user_test(user):
    return user.is_anonymous == False

# auxiliary function that checks for the overall category percentage and emails the user if overall percent is greater than 90%
# also changes the flags for has_email_sent to prevent multiple emails being sent when adding new expenditures while over the weekly limit
def category_progress_email_check():

    """Function that will send an email to the user when one of their categories is close to their weekly limit"""
    """Limits the emails being sent to only when spending >=90% and has_email_sent=False to not fill up email inbox"""

    def _make_percent(num, cat_name, user):
                denom = Category.objects.filter(users__id = user.id).get(name=cat_name).week_limit
                percent = (100 * (float(num)/float(denom)))
                if percent > 100:
                    return 100
                return percent

    for user in User.objects.filter(is_staff=False, is_superuser=False):

        week_start = timezone.now().date() + relativedelta(weekday=MO(-1))
        week_end = week_start + relativedelta(weekday=SU(1))
        categories = Category.objects.filter(is_overall = False).filter(users__id = user.id)
        val_dict = {}
        for category in categories:
            val_dict[category.name] = 0
        expenditures = Expenditure.objects.filter(user=user, date_created__gte = week_start, date_created__lte = week_end, is_binned = False)
        for expenditure in expenditures:
            val_dict[expenditure.category.name] += expenditure.expense#dict from category name -> total expense
        overall_spend = sum(val_dict.values())
        overall = Category.objects.filter(users__id = user.id, is_overall=True)
        overall_percent = _make_percent(overall_spend, overall.get(name="Overall"), user)

        if overall_percent >= 90 and not user.has_email_sent:
            user.has_email_sent = True
            user.save()
            Emailer.send_spending_limit_notification("Spending Limits", user.email, user.first_name)
        elif overall_percent < 90 and user.has_email_sent:
            user.has_email_sent = False
            user.save()
        else:
            pass

# redirects user to landing page when logged in
# also creates expenditure creation activity for activity page
# also returns cumulative expenditure data for the graphs and data cards
@user_passes_test(user_test, login_url='log_out')
@anonymous_prohibited
def landing_page(request):
    if request.method == 'POST':
        form=ExpenditureForm(request.POST, request.FILES, r=request)
        if form.is_valid():
            expenditure = form.save(commit=False)
            expenditure.user = request.user
            expenditure.save()
            category_progress_email_check()
            activity_name = f'You\'ve created a \"{expenditure.title}\" expenditure of \"{expenditure.category.name}\" category with {expenditure.expense} expense'
            user_activity = Activity.objects.create(user=request.user, image = "images/expenditure.png", name = activity_name, points = 15)
            activity_points(request, user_activity.points)
            return redirect('landing_page')
    else:

        form = ExpenditureForm(r=request)
    objectList = Expenditure.objects.filter(user=request.user, is_binned=False)

    '''Data for list display'''
    spendingList = objectList.order_by('-date_created')[0:19]

    if spendingList.count() == 1:
        try:
            try:
                UserAchievement.objects.create(user=request.user, achievement=Achievement.objects.get(name="First expenditure"))
            except ObjectDoesNotExist:
                pass
            user_activity = Activity.objects.create(user=request.user, image = "badges/first_expenditure.png", name = "You've earned \"First expenditure\" achievement", points = 15)
            activity_points(request, user_activity.points)
        except IntegrityError:
            pass

    '''Data for chart display'''
    current_date = date.today()
    objectList7 = objectList.filter(date_created__range=(
        current_date-timezone.timedelta(days=6), current_date+timezone.timedelta(days=1)))
    objectList30 = objectList.filter(date_created__range=(
        current_date-timezone.timedelta(days=29), current_date+timezone.timedelta(days=1)))
    objectList90 = objectList.filter(date_created__range=(
        current_date-timezone.timedelta(days=89), current_date+timezone.timedelta(days=1)))
    dataTuple7 = getAllList(objectList7, 7, request)
    dataTuple30 = getAllList(objectList30, 30, request)
    dataTuple90 = getAllList(objectList90, 90, request)
    categoryList = {7: dataTuple7[0], 30: dataTuple30[0], 90: dataTuple90[0]}
    expenseList = {7: dataTuple7[1], 30: dataTuple30[1], 90: dataTuple90[1]}
    dateList = {7: dataTuple7[2], 30: dataTuple30[2], 90: dataTuple90[2]}
    dailyExpenseList = {7: dataTuple7[3], 30: dataTuple30[3], 90: dataTuple90[3]}
    cumulativeExpenseList = {7: dataTuple7[4], 30: dataTuple30[4], 90: dataTuple90[4]}

    try:
        user_level = UserLevel.objects.get(user=request.user)
    except UserLevel.DoesNotExist:
        try:
            Level.objects.get(name = "Level 1")
        except Level.DoesNotExist:
            Level.objects.create(name="Level 1", description="Description of level 1", required_points=100)
        user_level = UserLevel(user=request.user, level=Level.objects.get(name = "Level 1"), points=0)
        user_level.save()

    current_level = user_level.level
    current_level_name = current_level.name
    current_points = user_level.points

    next_level_points = current_level.required_points
    if current_points >= next_level_points:
        progress_percentage = 100
    else:
        progress_percentage = int(100+(current_points-next_level_points))

    user_tier_colour = get_user_tier_colour(request.user)
    reached_tiers = get_reached_tiers(UserLevel.objects.get(user=request.user).points)
    if reached_tiers:
        user_tier_name, tier_data = reached_tiers.popitem()
    else:
        user_tier_name = ""

    try:
        avatar = 'avatar/' + Avatar.objects.get(user=request.user).file_name
        avatar_path = os.path.join(settings.STATICFILES_DIRS[0], avatar)
        if not os.path.exists(avatar_path):
            avatar = 'avatar/default_avatar.png'
    except Avatar.DoesNotExist:
        avatar = 'avatar/default_avatar.png'

    return render(request, 'landing_page.html', {
        'form': form,
        'spendings': spendingList,
        'categoryList': categoryList,
        'expenseList': expenseList,
        'dateList': dateList,
        'dailyExpenseList': dailyExpenseList,
        'cumulativeExpenseList': cumulativeExpenseList,
        'current_level_name': current_level_name,
        'current_points': current_points,
        'progress_percentage': progress_percentage,
        'user_tier_colour': user_tier_colour,
        'user_tier_name': user_tier_name,
        'avatar': avatar,
    })

# returns list of categories and expenditures to be used as graph axis data
def getCategoryAndExpenseList(objectList, request):
    categoryList = []
    expenseList = []
    for x in request.user.available_categories.all():
        tempList = objectList.filter(category=x, is_binned=False)
        if tempList.exists():
            categoryList.append(x)
        tempInt = 0
        for y in tempList:
            tempInt += y.expense
        expenseList.append(tempInt)
    return categoryList, expenseList

# returns list of dates and expenses to be used as graph axis data
def getDateListAndDailyExpenseList(objectList, num):
    dateList = []
    dailyExpenseList = []
    for x in objectList.filter(is_binned=False).order_by('date_created'):
        dateList.append(x.date_created.date())
        dailyExpenseList.append(x.expense)
    for x in range(0, len(dateList)):
        try:
            while dateList[x] == dateList[x+1]:
                dailyExpenseList[x] += dailyExpenseList[x+1]
                dailyExpenseList.pop(x+1)
                dateList.pop(x+1)
        except IndexError:
            break

    start_date = date.today()-timezone.timedelta(days=num-1)
    end_date = date.today()
    current_date = start_date
    while current_date <= end_date:
        if current_date not in dateList:
            dateList.append(current_date)
            dateList.sort()
            dailyExpenseList.insert(dateList.index(current_date), 0)
        current_date += timezone.timedelta(days=1)

    return dateList, dailyExpenseList

# returns cumulative value of all expenses of a user
def getCumulativeExpenseList(objectList, dailyExpenseList):
    cumulativeExpenseList = []
    cumulativeExpense = 0
    for x in dailyExpenseList:
        cumulativeExpense += x
        cumulativeExpenseList.append(cumulativeExpense)
    return cumulativeExpenseList

# returns all category and expenditures
def getAllList(objectList, num, request):
    first = getCategoryAndExpenseList(objectList, request)
    cat = first[0]
    exp = first[1]
    second = getDateListAndDailyExpenseList(objectList, num)
    dat = second[0]
    dai = second[1]
    cum = getCumulativeExpenseList(objectList, dai)
    return cat, exp, dat, dai, cum

# redirects user on successful password reset
def change_password_success(request):
    Activity.objects.create(user=request.user, image = "images/edit.png", name = "You've changed your password")
    return render(request, 'change_password_success.html')

# class based view for editing user data
class UserEditView(generic.UpdateView):
    form_class = EditUserForm
    template_name = 'edit_user.html'
    success_url = reverse_lazy('landing_page')

    def get_object(self):
        return self.request.user

    def get_initial(self):
        user = self.get_object()
        return {'email': user.email, 'first_name': user.first_name, 'last_name': user.last_name}

    def form_valid(self, form):
        user = self.get_object()
        old_email = form.initial['email']
        old_first_name = form.initial['first_name']
        old_last_name = form.initial['last_name']

        if old_email != user.email:
            activity_name = f'You\'ve changed your email from {old_email} to {user.email}'
            Activity.objects.create(user=self.request.user, image = "images/edit.png", name = activity_name)
        if old_first_name != user.first_name:
            activity_name = f'You\'ve changed your first name from {old_first_name} to {user.first_name}'
            Activity.objects.create(user=self.request.user, image = "images/edit.png", name = activity_name)
        if old_last_name != user.last_name:
            activity_name = f'You\'ve changed your last name from {old_last_name} to {user.last_name}'
            Activity.objects.create(user=self.request.user, image = "images/edit.png", name = activity_name)

        return super().form_valid(form)

# redirects to forum home
# returns lists for forum categories, number of posts, number of users, number of categories and the last post made
@anonymous_prohibited
def forum_home(request):
    all_forum_categories = Forum_Category.objects.all()
    num_posts = Post.objects.all().count()
    num_users = User.objects.all().count()
    num_categories = all_forum_categories.count()

    if Post.objects.count() == 0:
        last_post = None
    else:
        last_post = Post.objects.latest('date')

    context = {
        "all_forum_categories": all_forum_categories,
        "num_posts": num_posts,
        "num_users": num_users,
        "num_categories": num_categories,
        "last_post": last_post,
        "title": "Forum Home",
    }
    return render(request, 'forum/forum_home.html', context)

# redirects user to posts list view
# returns all posts and forum categories to the post view
def posts(request, slug):
    category = get_object_or_404(Forum_Category, slug=slug)
    posts = Post.objects.filter(approved=True, forum_categories=category).order_by('id')
    paginator = Paginator(posts, 5)
    page = request.GET.get("page")
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    context = {
        "posts": posts,
        "forum": category,
        "title": "Posts",
    }

    return render(request, 'forum/posts.html', context)

# Displays details of a forum posts -> Post, comments and replies.)
def detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    posts = Post.objects.all()
    author = request.user
    points = {}
    avatars = {}
    tier_colours = {}
    user_levels = {}
    user_tier_names = {}


    if request.user.is_authenticated:
        if "comment-form" in request.POST:
            comment = request.POST.get("comment")
            media = request.FILES.get("media")
            new_comment, created = Comment.objects.get_or_create(user=author, content=comment, media=media)
            post.comments.add(new_comment.id)
            create_forum_activity(request, "made", post, new_comment)
            check_forum_user_achievements(request)

            if(request.user != post.user):
                create_notification(request, post.user, 'comment', slug)

        if "reply-form" in request.POST:
            reply = request.POST.get("reply")
            media = request.FILES.get("media")
            comment_id = request.POST.get("comment-id")
            comment_obj = Comment.objects.get(id=comment_id)
            new_reply, created = Reply.objects.get_or_create(user=author, content=reply, media=media)
            comment_obj.replies.add(new_reply.id)
            create_forum_activity(request, "left", post, comment_obj, new_reply)
            check_forum_user_achievements(request)

            if(request.user != comment_obj.user):
                create_notification(request, comment_obj.user, 'reply', slug)

    else:
        messages.info(request, 'You need to be logged in to post')
        return redirect("home")

    for comment in post.comments.all():
        points, avatars, tier_colours, user_levels, user_tier_names = get_forum_user_info(points, avatars, tier_colours, user_levels, user_tier_names, comment)
        for reply in comment.replies.all():
            points, avatars, tier_colours, user_levels, user_tier_names = get_forum_user_info(points, avatars, tier_colours, user_levels, user_tier_names, reply)

    points, avatars, tier_colours, user_levels, user_tier_names = get_forum_user_info(points, avatars, tier_colours, user_levels, user_tier_names, post)

    context = {
        "post": post,
        "title": post.title,
        "points": points,
        "avatars": avatars,
        "tier_colours": tier_colours,
        "user_levels": user_levels,
        "user_tier_names": user_tier_names,
        "posts": posts,
    }
    update_views(request, post)
    return render(request, 'forum/detail.html', context)


# Moves to notification page and updates notifications.
@anonymous_prohibited
def notifications(request):

    if "noti-form" in request.POST:
        noti_id = request.POST.get("noti-id")
        noti_obj = Notification.objects.get(id=noti_id)
        noti_obj.is_read = True
        noti_obj.save()

    return render(request, 'notifications.html')

# displays user info of other users when clicking on their name in a forum post
def get_forum_user_info(points, avatars, tier_colours, user_levels, user_tier_names, forum_object):
    user_level = UserLevel.objects.get(user=forum_object.user)
    user_points = user_level.points
    points[forum_object.user.id] = user_points
    try:
        avatars[forum_object.user.id] = 'avatar/' + Avatar.objects.get(user=forum_object.user).file_name
        avatar_path = os.path.join(settings.STATICFILES_DIRS[0], avatars[forum_object.user.id])
        if not os.path.exists(avatar_path):
            avatars[forum_object.user.id] = 'avatar/default_avatar.png'
    except Avatar.DoesNotExist:
        avatars[forum_object.user.id] = 'avatar/default_avatar.png'
    tier_colours[forum_object.user.id] = get_user_tier_colour(forum_object.user)
    user_levels[forum_object.user.id] = user_level.level.name
    reached_tiers = get_reached_tiers(user_points)
    if reached_tiers:
        user_tier_names[forum_object.user.id], tier_data = reached_tiers.popitem()
    else:
        user_tier_names[forum_object.user.id] = ""
    return points, avatars, tier_colours, user_levels, user_tier_names

# creates post object from user form input data and redirects to a new page display the created post
@anonymous_prohibited
def create_post(request):
    context = {}
    form = PostForm(request.POST or None, request.FILES or None)
    if request.method == "POST":
        if form.is_valid():
            author = request.user
            new_post = form.save(commit=False)
            new_post.user = author
            new_post.save()
            form.save_m2m()
            create_forum_activity(request, "created", new_post)
            check_forum_user_achievements(request)
            return redirect(new_post.get_url())
    context.update({
        "form": form,
        "title": "Create New Post"
    })
    return render(request, "forum/create_post.html", context)

# deletes a post from the database
@anonymous_prohibited_with_id
def delete_post(request, id):
    try:
        post = Post.objects.get(id = id)
        comments = post.comments.all()
        for comment in comments:
            comment.replies.all().delete()
        comments.all().delete()
        create_forum_activity(request, "deleted", post)
        post.delete()
    except Post.DoesNotExist:
        pass
    return redirect('forum_home')

# validates and saves edited form data
@anonymous_prohibited_with_id
def edit_post(request, id):
    try:
        post = Post.objects.get(id=id)
        if request.method == "POST":
            form = PostForm(request.POST, request.FILES, instance=post)
            if form.is_valid():
                post = form.save(commit=False)
                post.edited_at = timezone.now()
                post.save()
                form.save_m2m()
                create_forum_activity(request, "edited", post)
                return redirect(post.get_url())
        else:
            form = PostForm(instance=post)
    except Post.DoesNotExist:
        return redirect('forum_home')
    return render(request, 'forum/edit_post.html', {'form' : form})

# deletes comment from the database
@anonymous_prohibited_with_id
def delete_comment(request, id):
    try:
        comment = Comment.objects.get(id=id)
        post = Post.objects.get(comments=comment)
        post.comments.remove(comment)
        comment.replies.all().delete()
        create_forum_activity(request, "deleted", post, comment)
        comment.delete()
        return redirect(post.get_url())
    except Comment.DoesNotExist:
        pass
    return redirect('forum_home')

# validates and saves form input data when editing a comment
@anonymous_prohibited_with_id
def edit_comment(request, id):
    try:
        comment = Comment.objects.get(id=id)
        post = Post.objects.get(comments=comment)
        if request.method == "POST":
            content = request.POST.get("content")
            media = request.FILES.get("media")
            media_clear = request.POST.get("media-clear")
            if media:
                comment.media = media
            elif media_clear:
                comment.media.delete()
                comment.media = None
            comment.content = content
            comment.edited_at = timezone.now()
            comment.save()
            create_forum_activity(request, "edited", post, comment)
        return redirect(post.get_url())
    except Comment.DoesNotExist:
        return redirect('forum_home')

# deletes a user reply from the database
@anonymous_prohibited_with_id
def delete_reply(request, id):
    try:
        reply = Reply.objects.get(id=id)
        comment = Comment.objects.get(replies=reply)
        comment.replies.remove(reply)
        post = Post.objects.get(comments=comment)
        create_forum_activity(request, "deleted", post, comment, reply)
        reply.delete()
        return redirect(post.get_url())
    except Reply.DoesNotExist:
        pass
    return redirect('forum_home')

# validates and saves user form data when editing a reply
@anonymous_prohibited_with_id
def edit_reply(request, id):
    try:
        reply = Reply.objects.get(id=id)
        comment = Comment.objects.get(replies=reply)
        post = Post.objects.get(comments=comment)
        if request.method == "POST":
            content = request.POST.get("content")
            media = request.FILES.get("media")
            media_clear = request.POST.get("media-clear")
            if media:
                reply.media = media
            elif media_clear:
                reply.media.delete()
                reply.media = None
            reply.content = content
            reply.edited_at = timezone.now()
            reply.save()
            create_forum_activity(request, "edited", post, comment, reply)
        return redirect(post.get_url())
    except Reply.DoesNotExist:
        return redirect('forum_home')

# creates activity objects of forum actions e.g. commenting, replying and making posts on the forum to be displayed on the activity page
def create_forum_activity(request, action, post, *args):
    category_names = [category.title for category in post.forum_categories.all()]
    forum_name = "forums" if len(category_names) > 1 else "forum"
    dots = ""

    if len(args) == 1:
        comment_content = args[0].content.split()
        if len(comment_content) > 5:
            dots = "..."
        for i in range(0, len(comment_content)):
            word = comment_content[i]
            if len(word) > 45:
                comment_content[i] = word[0:10] + "..."
        activity_name = f'You\'ve {action} \"{" ".join(comment_content[:5])}{dots}\" comment on the \"{post.title}\" post in {", ".join(category_names)} {forum_name}'
    elif len(args) == 2:
        reply_content = args[1].content.split()
        if len(reply_content) > 5:
            dots = "..."
        for i in range(0, len(reply_content)):
            word = reply_content[i]
            if len(word) > 45:
                reply_content[i] = word[0:10] + "..."
        activity_name = f'You\'ve {action} \"{" ".join(reply_content[:5])}{dots}\" reply on the \"{post.title}\" post in {", ".join(category_names)} {forum_name}'
    else:
        activity_name = f'You\'ve {action} \"{post.title}\" post in {", ".join(category_names)} {forum_name}'

    points = 15 if action in ["created", "made", "left"] else 0
    user_activity = Activity.objects.create(user=request.user, image="images/forum.png",
                                             name=activity_name, points=points)
    if points != 0:
        activity_points(request, user_activity.points)

# redirects and shows another users achievements when clicking on them in the forum
def check_forum_user_achievements(request):
    post_count = Post.objects.filter(user=request.user).count()
    reply_count = Reply.objects.filter(user=request.user).count()
    comment_count = Comment.objects.filter(user=request.user).count()
    total = post_count + reply_count + comment_count
    forum_achievements = {1: ("Junior forumite", 10), 10: ("Active contributor", 50), 100: ("Forum veteran", 100)}

    if total in forum_achievements:
        achievement_name, points = forum_achievements[total]
        try:
            try:
                UserAchievement.objects.create(user=request.user,
                                               achievement=Achievement.objects.get(name=achievement_name))
            except ObjectDoesNotExist:
                pass
            user_activity = Activity.objects.create(user=request.user, image="badges/forum.png",
                                                        name=f"You've earned \"{achievement_name}\" achievement",
                                                        points=points)
            activity_points(request, user_activity.points)
        except IntegrityError:
            pass

# returns the last 10 posts on the database
@anonymous_prohibited
def latest_posts(request):
    posts = Post.objects.all().filter(approved=True)[:10]
    context = {
        "posts": posts,
        "title": "Latest 10 Posts"
    }
    return render(request, "forum/latest_posts.html", context)

# Returns the results of a forum search.

# returns the forum post list after filtering with the search bar input
# only shows posts relevant to what the user input
def search_result(request):
    query = request.GET.get('q')
    results = Post.objects.filter(title__icontains=query).order_by('id')

    paginator = Paginator(results, 5)
    page = request.GET.get('page')
    objects = paginator.get_page(page)

    context = {
        'query': query,
        'objects': objects,
    }
    return render(request, 'forum/search.html', context)

# returns all the current challenges in the database to return for display on the challenge list page
@anonymous_prohibited
def challenge_list(request):
    challenges = Challenge.objects.all()
    return render(request, 'challenge_list.html', {'challenges': challenges})

# returns all the current achievements in the database to return for display on the achievement list page
@anonymous_prohibited
def achievement_list(request):
    achievements = Achievement.objects.all()
    return render(request, 'achievement_list.html', {'achievements': achievements})

# returns description of the achievement got by the id argument
def challenge_details(request, id):
    challenge = Challenge.objects.get(id=id)
    return render(request, 'challenge_details.html', {'challenge': challenge})

# enters a user into a challenge
# checks if user is already in challenge
def enter_challenge(request):
    try:
        if request.method == 'POST':
            challenge_id = request.POST['challenge_id']
            user_challenge = UserChallenge(user=request.user, challenge_id=challenge_id)
            user_challenge.save()
            user_activity = Activity.objects.create(user=request.user, image = "images/start.png", name = f'You\'ve entered \"{user_challenge.challenge.name}\" challenge', points = 15)
            activity_points(request, user_activity.points)
            complete_challenge(request, challenge_id)
        return redirect('my_challenges')
    except IntegrityError:
        messages.error(request, 'You have already entered this challenge.')
        return redirect('challenge_list')

# returns list of challenges the user has entered
@anonymous_prohibited
def my_challenges(request):
    user_challenges = UserChallenge.objects.filter(user=request.user)
    return render(request, 'my_challenges.html', {'user_challenges': user_challenges})

# marks challenge completed and gives the set points
# also checks for number of challenges completed, giving the user achievements for 1 and 10 completed challenges
def complete_challenge(request, id):
    try:
        user_challenge = UserChallenge.objects.get(user=request.user, challenge_id=id)
    except UserChallenge.DoesNotExist:
        user_challenge = None
    if user_challenge is not None:
        if user_challenge.date_completed is not None:
            return redirect('challenge_list')

        user_challenge.date_completed = timezone.now()
        user_challenge.save()

        user_challenges_count = UserChallenge.objects.filter(user=request.user).count()
        try:
            if user_challenges_count == 1:
                UserAchievement.objects.create(user=request.user, achievement=Achievement.objects.get(name="Wise spender"))
                user_activity = Activity.objects.create(user=request.user, image = "badges/wise_spender.png", name = "You've earned \"Wise spender\" achievement", points = 15)
                create_achievement_notification(request, request.user, "achievement", UserAchievement.achievement)
                activity_points(request, user_activity.points)
            elif user_challenges_count == 10:
                UserAchievement.objects.create(user=request.user, achievement=Achievement.objects.get(name="Superstar"))
                user_activity = Activity.objects.create(user=request.user, image = "badges/super_star.png", name = "You've earned \"Superstar\" achievement", points = 150)
                create_achievement_notification(request, request.user, "achievement", UserAchievement.achievement)
                activity_points(request, user_activity.points)
        except ObjectDoesNotExist:
            pass

        Activity.objects.create(user=request.user, image = "images/completed.png", name = f'You\'ve completed \"{user_challenge.challenge.name}\" challenge', points = user_challenge.challenge.points)

        try:
            user_level = UserLevel.objects.get(user=request.user)
            user_level.points += user_challenge.challenge.points
            user_level.save()
        except UserLevel.DoesNotExist:
            challenge_points = user_challenge.challenge.points
            new_user_level = UserLevel(user=request.user, level=Level.objects.get(name = f"Level {floor(challenge_points / 100) + 1}"), points=challenge_points)
            new_user_level.save()
        update_user_level(user=request.user)

    return redirect('challenge_list')

# assigns points for any point giving actions to the users level
def activity_points(request, points):
    try:
        user_level = UserLevel.objects.get(user=request.user)
        user_level.points += points
        user_level.save()
        update_user_level(request.user)
    except ObjectDoesNotExist:
        pass

# creates a new level object when a user reaches a level that has not been reached before
# assigns a level to user when levelled up when level object already exists
def update_user_level(user):
    user_level = UserLevel.objects.get(user=user)
    total_points = user_level.points

    try:
        current_level = Level.objects.get(name = f"Level {floor(total_points / 100) + 1}")
        if user_level.level.id < current_level.id:
            Activity.objects.create(user=user, image = "images/level_up.png", name = f'You\'ve leveled up to {current_level.name}')
        user_level.level = current_level
        user_level.save()
    except Level.DoesNotExist:
        last_level = Level.objects.order_by('-required_points').first()
        last_level_points = last_level.required_points
        last_level_number = int(last_level_points/100)
        num_levels = floor((total_points - last_level_points)/100)

        for i in range(1, num_levels + 2):
            name = f'Level {last_level_number+i}'
            description = f'Description of level {last_level_number+i}'
            required_points = last_level_points + (i * 100)
            new_level = Level.objects.create(name=name, description=description, required_points=required_points)
            if (user_level.level.id < new_level.id):
                Activity.objects.create(user=user, image = "images/level_up.png", name = f'You\'ve leveled up to {new_level.name}')
            new_level.save()

        current_level = Level.objects.get(name = f"Level {floor(total_points / 100) + 1}")
        user_level.level = current_level
        user_level.save()

# creates url for avatar to be shared on external sites
def share_avatar(request):
    svg = "avatar"
    name = "My avatar"
    description = "Avatar created in Galin's Spending Tracker"
    url = request.build_absolute_uri(reverse('profile', args=[str(request.user.id)]))
    text = "Check out my avatar created in Galin's Spending Tracker"
    return share(request, svg, name, description, url, text)

# creates url for challenges to be shared on external sites
def share_challenge(request, id):
    user_challenge = UserChallenge.objects.get(id=id)
    name = user_challenge.challenge.name
    description = user_challenge.challenge.description
    url = request.build_absolute_uri(reverse('challenge_details', args=[str(user_challenge.challenge.id)]))
    text = f"I'm doing the \"{name}\" challenge on Galin's Spending Tracker"
    return share(request, user_challenge, name, description, url, text)

# creates url for achievement to be shared on external sites
def share_achievement(request, id):
    user_achievement = UserAchievement.objects.get(id=id)
    name = user_achievement.achievement.name
    description = user_achievement.achievement.description
    url = request.build_absolute_uri(reverse('profile', args=[str(request.user.id)]))
    text = f"I've earned the \"{name}\" achievement on Galin's Spending Tracker"
    return share(request, user_achievement, name, description, url, text)

# creates url for post to be shared on external sites
def share_post(request, id):
    post = Post.objects.get(id=id)
    name = post.title
    post_user = User.objects.get(id=post.user.id)
    if post_user.username:
        user_name = post_user.username
    else:
        user_name = post_user.first_name + " " + post_user.last_name
    description = "Forum post on Galin's Spending Tracker"
    url = request.build_absolute_uri(post.get_url())
    text = f"Check out \"{name}\" post by {user_name} on Galin's Spending Tracker"
    return share(request, post, name, description, url, text)

# creates url for comment to be shared on external sites
def share_comment(request, id):
    comment = Comment.objects.get(id=id)
    post = Post.objects.get(comments=comment)
    name = comment.content
    comment_user = User.objects.get(id=comment.user.id)
    if comment_user.username:
        user_name = comment_user.username
    else:
        user_name = comment_user.first_name + " " + comment_user.last_name
    description = "Forum comment on Galin's Spending Tracker"
    url = request.build_absolute_uri(post.get_url())
    text = f"Check out \"{name}\" comment by {user_name} on \"{post.title}\" post in Galin's Spending Tracker"
    return share(request, comment, name, description, url, text)

# creates url for reply to be shared on external sites
def share_reply(request, id):
    reply = Reply.objects.get(id=id)
    comment = Comment.objects.get(replies=reply)
    post = Post.objects.get(comments=comment)
    name = reply.content
    reply_user = User.objects.get(id=reply.user.id)
    if reply_user.username:
        user_name = reply_user.username
    else:
        user_name = reply_user.first_name + " " + reply_user.last_name
    description = "Forum reply on Galin's Spending Tracker"
    url = request.build_absolute_uri(post.get_url())
    text = f"Check out \"{name}\" reply by {user_name} on \"{post.title}\" post in Galin's Spending Tracker"
    return share(request, reply, name, description, url, text)

def share(request, *args):
    if args:
        user_object = args[0]
        name = args[1]
        description = args[2]
        url = args[3]
        text = args[4]
        facebook_params = {
            'app_id': '1437874963685388',
            'display': 'popup',
            'href': 'facebook.com'
        }
        twitter_params = {
            'url': url,
            'text': text
        }
        share_urls = {
            'facebook': 'https://www.facebook.com/dialog/share?' + urlencode(facebook_params),
            'twitter': 'https://twitter.com/share?' + urlencode(twitter_params),
            'forum': request.build_absolute_uri(reverse('create_post'))
        }

        if isinstance(user_object, UserAchievement):
            media = user_object.achievement.badge
            return render(request, 'share.html', {'name': name, 'description': description, 'share_urls': share_urls, 'type': 'achievement', 'media': media})
        elif isinstance(user_object, UserChallenge):
            return render(request, 'share.html', {'name': name, 'description': description, 'share_urls': share_urls, 'type': 'challenge'})
        elif isinstance(user_object, str):
            user_tier_colour = get_user_tier_colour(request.user)
            try:
                media = 'avatar/' + Avatar.objects.get(user=request.user).file_name
                avatar_path = os.path.join(settings.STATICFILES_DIRS[0], media)
                if not os.path.exists(avatar_path):
                    media = 'avatar/default_avatar.png'
            except Avatar.DoesNotExist:
                media = 'avatar/default_avatar.png'
            return render(request, 'share.html', {'name': name, 'description': description, 'share_urls': share_urls, 'type': 'avatar', 'user_tier_colour': user_tier_colour, 'media': media})
        elif isinstance(user_object, Post):
            media = user_object.media
            return render(request, 'share.html', {'name': name, 'description': description, 'share_urls': share_urls, 'type': 'post', 'media': media})
        elif isinstance(user_object, Comment):
            media = user_object.media
            return render(request, 'share.html', {'name': name, 'description': description, 'share_urls': share_urls, 'type': 'comment', 'media': media})
        elif isinstance(user_object, Reply):
            media = user_object.media
            return render(request, 'share.html', {'name': name, 'description': description, 'share_urls': share_urls, 'type': 'reply', 'media': media})
        else:
            return redirect('landing_page')
    else:
        return redirect('landing_page')

def handle_share(request):
    type = unquote(request.GET.get('type'))
    name = unquote(request.GET.get('name'))
    site = unquote(request.GET.get('site'))
    share_url = unquote(request.GET.get('share_url'))
    user_activity = Activity.objects.create(user=request.user, image = "images/share.png", name = f'You\'ve shared \"{name}\" {type} post on {site}', points = 15)
    activity_points(request, user_activity.points)
    try:
        try:
            UserAchievement.objects.create(user=request.user, achievement=Achievement.objects.get(name="First share"))
        except ObjectDoesNotExist:
            pass
        user_activity = Activity.objects.create(user=request.user, image = "badges/first_share.png", name = "You've earned \"First share\" achievement", points = 15)
        activity_points(request, user_activity.points)
    except IntegrityError:
        pass
    return redirect(share_url)

# returns list of achievements the user has
@anonymous_prohibited
def my_achievements(request):
    user_achievements = UserAchievement.objects.filter(user=request.user)
    return render(request, 'my_achievements.html', {'user_achievements': user_achievements})

# returns list of all activity objects created for a user
@login_required
def my_activity(request):
    num_items = request.GET.get('num_items')
    if num_items == 'all':
        user_activity = Activity.objects.filter(user=request.user).order_by('-time')
    else:
        user_activity = Activity.objects.filter(user=request.user).order_by('-time')[:int(num_items)]
    return render(request, 'my_activity.html', {'user_activity': user_activity})

# returns all customisation options of user avatar
@anonymous_prohibited
@cache_control(no_store=True)
def my_avatar(request):
    locked_items = get_locked_items(request)
    user_tier_colour = get_user_tier_colour(request.user)
    tier_info = get_tier_info()
    create_avatar(request)
    colours = get_avatar_colours()
    components = {}
    components_copy = {}

    required_items_selected = check_required_items(request)

    if not required_items_selected and 'random' not in request.GET.keys():
        messages.info(request, 'You need to select at least body, face and head for avatar to be saved.')

    for category in ['eyewear', 'body', 'face', 'facial-hair', 'head']:
        components[category] = []
        components_copy[category] = []

        category_path = os.path.join(settings.STATICFILES_DIRS[0], 'avatar', category)
        for file_name in os.listdir(category_path):
            if file_name.endswith('.svg'):
                components[category].append(file_name)
                # fill components copy dictionary for randomising the avatar
                if 'random' in request.GET.keys():
                    components_copy[category].append(file_name)
                    # remove locked items from the components copy based on the user tier
                    if file_name in locked_items.keys():
                        components_copy[category].remove(file_name)

        # choose a random component from each category
        if 'random' in request.GET.keys():
            random_component = random.choice(components_copy[category])
            # make the request query dictionary mutable and update it with random components
            query_dict = QueryDict('', mutable=True)
            query_dict.update(request.GET)
            query_dict[category] = random_component[:-4]
            request.GET = query_dict

    # choose a random colour for each coloured component
    if 'random' in request.GET.keys():
        for category in colours.keys():
            random_colour = random.choice(colours[category])
            # update the mutable query dictionary
            query_dict.update(request.GET)
            query_dict[category] = random_colour
            request.GET = query_dict

        # create random avatar with the filled query dictionary passed in the request
        create_avatar(request)
        check_required_items(request)
        create_avatar_activity(request)

    return render(request, 'my_avatar.html', {'components': components, 'colours': colours, 'locked_items': locked_items, 'tier_info': tier_info, 'user_tier_colour': user_tier_colour})

# checks if user avatar has all the required customisations to be saved
def check_required_items(request):
    required_items_selected = True
    current_template = Avatar.objects.get(user=request.user).current_template

    if current_template.endswith('.svg'):
        avatar_file_path = os.path.join(settings.STATICFILES_DIRS[0], 'avatar', current_template)
        user_svg = open(avatar_file_path, 'r').read()

        for category in ['body', 'face', 'head']:
            category_g_block = re.search(fr'<g id="{category}"[^>]*>', user_svg)
            if category_g_block:
                start_index = category_g_block.end()
                end_index = user_svg.find('</g>', start_index)
                category_content = user_svg[start_index:end_index]
                if not category_content.strip():
                    required_items_selected = False

        if not required_items_selected:
            avatar = Avatar.objects.get(user=request.user)
            avatar.file_name = "default_avatar.png"
            avatar.save()
        else:
            avatar = Avatar.objects.get(user=request.user)
            avatar.file_name = avatar.current_template
            avatar.save()

    return required_items_selected

# creates avatar from user customisations
@login_required
@cache_control(no_store=True)
def create_avatar(request):
    try:
        avatar = Avatar.objects.get(user=request.user)
    except ObjectDoesNotExist:
        avatar = create_avatar_object(request)

    try:
        user_svg_path = os.path.join(settings.STATICFILES_DIRS[0], 'avatar', avatar.current_template)
        user_svg = open(user_svg_path, 'r').read()
    except OSError:
        avatar.delete()
        avatar = create_avatar_object(request)
        user_svg_path = os.path.join(settings.STATICFILES_DIRS[0], 'avatar', avatar.current_template)
        user_svg = open(user_svg_path, 'r').read()

    for category, component in request.GET.items():
        if category in ['skin', 'accessories', 'shirt', 'hair', 'background', 'clear']:
            if category in ['background', 'clear']:
                colour_blocks = re.findall(r'<rect\s+id="background".*?>', user_svg)
            else:
                colour_blocks = re.findall(fr'<path id="{category}"[^>]*>', user_svg)
            for colour_block in colour_blocks:
                fill_param = re.search(r'fill="([^"]+)"', colour_block)
                if category == "clear":
                    component = "#ffffff"
                new_fill_param = f'fill="{component}"'
                block_with_new_fill_param = colour_block.replace(fill_param.group(0), new_fill_param)
                user_svg = user_svg.replace(colour_block, block_with_new_fill_param)
        if category in ['eyewear', 'body', 'face', 'facial-hair', 'head', 'clear']:
            if 'clear' in request.GET.keys():
                for category in ['eyewear', 'body', 'face', 'facial-hair', 'head']:
                   category_g_block = re.search(fr'<g id="{category}"[^>]*>', user_svg)
                   if category_g_block:
                        start_index = category_g_block.end()
                        end_index = user_svg.find('</g>', start_index)
                        user_svg = user_svg[:start_index] + user_svg[end_index:]
            else:
                svg_paths = get_svg_paths_for_component(category, component)
                category_g_block = re.search(fr'<g id="{category}"[^>]*>', user_svg)
                if category_g_block:
                    start_index = category_g_block.end()
                    end_index = user_svg.find('</g>', start_index)
                    user_svg = user_svg[:start_index] + svg_paths + user_svg[end_index:]

        if 'random' not in request.GET.keys():
            create_avatar_activity(request)

    open(user_svg_path, 'w').write(user_svg)
    return HttpResponse(user_svg, content_type='image/svg+xml')

# creates svg file for when a user customises their avatar
def create_avatar_object(request):
    template_path = os.path.join(settings.STATICFILES_DIRS[1], 'template.svg')
    template_svg = open(template_path, 'r').read()
    hash = hashlib.sha1()
    hash.update(str(timezone.now()).encode('utf-8'))
    avatar_file_name = f'avatar-{hash.hexdigest()[:-10]}.svg'
    avatar_file_path = os.path.join(settings.STATICFILES_DIRS[0], 'avatar', avatar_file_name)
    open(avatar_file_path, 'w').write(template_svg)
    avatar = Avatar.objects.create(user=request.user, file_name='default_avatar.png', current_template=avatar_file_name)
    return avatar

# finds svg file for a component customisation
def get_svg_paths_for_component(category, component):
    file_name = component + '.svg'
    item_path = os.path.join(settings.STATICFILES_DIRS[0], 'avatar', category, file_name)
    svg = open(item_path, 'r').read()
    path_tags = re.findall(r'<path.*?/>', svg)
    return ''.join(path_tags)

# returns all colours used for customisation
def get_avatar_colours():
    colours = {'skin': ['#694d3d', '#ae5d29', '#d08b5b', '#edb98a', '#ffdbb4'],
        'accessories': ['#78e185', '#8fa7df', '#9ddadb', '#e279c7', '#e78276', '#fdea6b', '#ffcf77'],
        'shirt': ['#78e185', '#8fa7df', '#9ddadb', '#e279c7', '#e78276', '#fdea6b', '#ffcf77'],
        'hair': ['#aa8866', '#debe99', '#241c11', '#4f1a00', '#9a3300'],
        'background': ['#b6e3f4', '#c0aede', '#d1d4f9', '#ffd5dc', '#ffdfbf']}
    return colours

# creates activity objects for when a user edits their avatar or creates an avatar.
def create_avatar_activity(request):
    if Activity.objects.filter(user=request.user, name="You've created an avatar").exists():
        user_activity = Activity.objects.create(user=request.user, image = "images/edit.png", name = "You've edited your avatar", points = 15)
        activity_points(request, user_activity.points)
    else:
        user_activity = Activity.objects.create(user=request.user, image = "images/avatar.png", name = "You've created an avatar", points = 15)
        activity_points(request, user_activity.points)
        try:
            try:
                UserAchievement.objects.create(user=request.user, achievement=Achievement.objects.get(name="Avatar master"))
                Activity.objects.create(user=request.user, image = "badges/avatar_master.png", name = "You've earned \"Avatar master\" achievement")
            except ObjectDoesNotExist:
                pass
        except IntegrityError:
            pass

def unlock_avatar(request):
    tier = request.GET.get('tier')
    for key, value in request.GET.items():
        if key in ['eyewear', 'body', 'face', 'facial-hair', 'head']:
            category = key
            file_name = request.GET.get(key) + '.svg'
            name = request.GET.get(key).replace("_", " ")
            return render(request, 'unlock_avatar.html', {'category': category, 'file_name': file_name, 'name': name, 'tier': tier})
    return redirect('my_avatar')

def get_tier_info():
    tier_info = {'bronze': ['400', '#f5922a'],
        'silver': ['900', '#c1cad1'],
        'gold': ['1900', '#ffb70a'],
        'platinum': ['3900', '#a9b1c8'],
        'diamond': ['9900', '#5e9bba']}
    return tier_info

def get_reached_tiers(points):
    tiers = get_tier_info()
    reached_tiers = {}
    for tier_name, tier_data in tiers.items():
        if points >= int(tier_data[0]):
            reached_tiers[tier_name] = tier_data
    return reached_tiers

def get_user_tier_colour(user):
    reached_tiers = get_reached_tiers(UserLevel.objects.get(user=user).points)
    if reached_tiers:
        tier_name, tier_data = reached_tiers.popitem()
        tier_colour = tier_data[1]
    else:
        tier_colour = '#ffffff'
    return tier_colour

def get_locked_items(request):
    tier_info = get_tier_info()
    locked_items = { 'eyepatch.svg': ['bronze', tier_info.get('bronze')[1]], 'sunglasses.svg': ['silver', tier_info.get('silver')[1]],
        'sunglasses_2.svg': ['silver', tier_info.get('silver')[1]], 'monster.svg': ['bronze', tier_info.get('bronze')[1]],
        'cyclops.svg': ['silver', tier_info.get('silver')[1]], 'full_3.svg': ['gold', tier_info.get('gold')[1]],
        'moustache_2.svg': ['bronze', tier_info.get('bronze')[1]], 'moustache_3.svg': ['bronze', tier_info.get('bronze')[1]],
        'mohawk.svg': ['platinum', tier_info.get('platinum')[1]], 'mohawk_2.svg': ['gold', tier_info.get('gold')[1]],
        'bear.svg': ['diamond', tier_info.get('diamond')[1]], 'hat_hip.svg': ['silver', tier_info.get('silver')[1]]}
    locked_items = update_locked_items(request, locked_items)
    return locked_items

def update_locked_items(request, locked_items):
    reached_tiers = get_reached_tiers(UserLevel.objects.get(user=request.user).points)
    for file_name, item_data in list(locked_items.items()):
        for tier_name, tier_data in reached_tiers.items():
            if tier_name == item_data[0]:
                del locked_items[file_name]
    return locked_items

@register.filter
def clean_title(category_name):
    return category_name.replace('-',' ').title()

@register.filter
def get_tier_name(locked_items, file_name):
    return locked_items.get(file_name)[0]

@register.filter
def get_tier_colour(locked_items, file_name):
    return locked_items.get(file_name)[1]

@register.filter
def get_forum_item(dictionary, user_id):
    return dictionary.get(user_id)

@register.filter
def time_since_custom(time):
    timedelta = timezone.now() - time
    elapsed_time = int(timedelta.total_seconds())
    if elapsed_time < 60:
        time_since = f"{elapsed_time} second{'s' if elapsed_time != 1 else ''} ago"
    elif elapsed_time < 3600:
        time_since = f"{elapsed_time // 60} minute{'s' if elapsed_time // 60 != 1 else ''} ago"
    elif elapsed_time < 86400:
        time_since = f"{elapsed_time // 3600} hour{'s' if elapsed_time // 3600 != 1 else ''} ago"
    elif elapsed_time < 604800:
        time_since = f"{elapsed_time // 86400} day{'s' if elapsed_time // 86400 != 1 else ''} ago"
    elif elapsed_time < 2592000:
        time_since = f"{elapsed_time // 604800} week{'s' if elapsed_time // 604800 != 1 else ''} ago"
    elif elapsed_time < 31536000:
        time_since = f"{elapsed_time // 2592000} month{'s' if elapsed_time // 2592000 != 1 else ''} ago"
    else:
        time_since = f"{elapsed_time // 31536000} year{'s' if elapsed_time // 31536000 != 1 else ''} ago"
    return time_since

# returns report data for categories and expenditures to be displayed in the report page
@anonymous_prohibited
def report(request):
    user = request.user
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
    else:
        today = timezone.now().date()
        start_date = today - timedelta(days=30)
        end_date = today + timedelta(days=1)
        form = ReportForm(initial={'start_date': start_date, 'end_date': end_date})

    expenditures = Expenditure.objects.filter(user=user,  is_binned=False, date_created__gte=start_date, date_created__lte=end_date)

    week_numbers = math.ceil((end_date - start_date).days / 7)
    day_number = (end_date - start_date).days
    category_counts = {}
    category_sums = {}
    category_limits = {}
    limit_sum_pair = {}
    over_list = []
    total_expense = 0
    most_expense = 0
    most_category = ''
    average_daily = 0
    most_daily = 0
    most_date = ''
    previous_total = 0
    previous_average = 0
    previous_total_difference = 0
    previous_average_difference = 0
    previous_start_date = start_date - timedelta(days=day_number)

    previous_expenditures = Expenditure.objects.filter(user=user,  is_binned=False, date_created__gte=previous_start_date, date_created__lte=start_date)
    for item in previous_expenditures:
        previous_total+=item.expense
    previous_average = round(previous_total/day_number,2)

    for expenditure in expenditures:
        total_expense += expenditure.expense
        category = expenditure.category.name
        limit = expenditure.category.week_limit
        if category in category_counts:
            category_counts[category] += 1
            category_sums[category] += expenditure.expense
            category_limits[category] = limit*week_numbers
        else:
            category_counts[category] = 1
            category_sums[category] = expenditure.expense
            category_limits[category] = limit*week_numbers

    for category in category_limits.keys():
        if category_sums.get(category)/total_expense*100 > most_expense:
            most_expense = round(category_sums.get(category)/total_expense*100, 2)
            most_category = category
        limit_sum_pair[category_limits.get(category)] = category_sums.get(category)
        if category_limits.get(category)<category_sums.get(category):
            over_list.append(category)


    limit_sum=0
    for value in category_limits.values():
        limit_sum+=value

    dateList = []
    dailyExpenseList = []
    for x in expenditures.order_by('date_created'):
        dateList.append(x.date_created.date())
        dailyExpenseList.append(x.expense)
    for x in range(0, len(dateList)):
        try:
            while dateList[x] == dateList[x+1]:
                dailyExpenseList[x] += dailyExpenseList[x+1]
                dailyExpenseList.pop(x+1)
                dateList.pop(x+1)
        except IndexError:
            break
    current_date = start_date
    while current_date <= end_date:
        if current_date not in dateList:
            dateList.append(current_date)
            dateList.sort()
            dailyExpenseList.insert(dateList.index(current_date), 0)
        current_date += timezone.timedelta(days=1)

    temp_sum  = 0
    for item in dailyExpenseList:
        if item>most_daily:
            most_daily = item
            most_date = dateList[dailyExpenseList.index(item)]
        temp_sum+=item
    average_daily = round(temp_sum/day_number, 2)

    if total_expense>previous_total:
        previous_total_difference = total_expense-previous_total
    else:
        previous_total_difference = previous_total-total_expense

    if average_daily>previous_average:
        previous_average_difference = float(average_daily)-float(previous_average)
    else:
        previous_average_difference = float(previous_average)-float(average_daily)

    previous_average_difference = round(previous_average_difference,2)

    context = {
        'expenditures': expenditures,
        'form': form,
        'category_counts': category_counts,
        'category_sums': category_sums,
        'category_limits': category_limits,
        'week_numbers': week_numbers,
        'day_number': day_number,
        'total_expense': total_expense,
        'start_date': start_date,
        'end_date': end_date,
        'limit_sum':limit_sum,
        'limit_sum_pair':limit_sum_pair,
        'over_list':over_list,
        'most_expense':most_expense,
        'most_category':most_category,
        'dateList':dateList,
        'dailyExpenseList':dailyExpenseList,
        'average_daily':average_daily,
        'most_daily':most_daily,
        'most_date':most_date,
        'previous_total':previous_total,
        'previous_average':previous_average,
        'previous_total_difference':previous_total_difference,
        'previous_average_difference':previous_average_difference,
    }
    return render(request, 'report.html', context)

# saves the position of created trees in the garden page
@csrf_exempt
@anonymous_prohibited
def save_item_position(request):
    if request.method == 'POST':
        user = request.user
        data = json.loads(request.body)
        tree = Tree.objects.get(tree_id=data['tree_id'])
        tree.x_position = data['x']
        tree.y_position = data['y']
        tree.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

# redirects user to the garden page
@anonymous_prohibited
def garden(request):
    currentUser = request.user
    user_level = UserLevel.objects.get(user=currentUser)
    treeNum = currentUser.trees
    pointTotal = user_level.points
    pointLeft = pointTotal - treeNum*100

    if request.method == 'POST':
        if pointLeft<100:
            messages.add_message(request, messages.ERROR, "Not Enough Points Available")
        else:
            currentUser.trees = treeNum+1
            currentUser.save()
            Tree.objects.create(
                user = currentUser,
                x_position=500,
                y_position=50,
            )
            Activity.objects.create(user=request.user, image = "images/smallTree.png", name = "You've planted a tree in Galin Environmental Project")

    treeNum = currentUser.trees
    check_tree_achievements(request, treeNum)
    pointTotal = user_level.points
    pointLeft = pointTotal - treeNum*100
    trees = Tree.objects.filter(user=currentUser)
    return render(request, 'garden.html',{
        "treeNum":treeNum,
        "pointTotal":pointTotal,
        "pointLeft":pointLeft,
        "trees":trees,
    })

# checks for achievements regarding how many trees have been planted in the garden page
def check_tree_achievements(request, treeNum):
    tree_achievements = {1: ("Planting pioneer", 10), 10: ("Forest friend", 50), 100: ("Green guardian", 100)}
    if treeNum in tree_achievements:
        achievement_name, points = tree_achievements[treeNum]
        try:
            try:
                UserAchievement.objects.create(user=request.user,
                                               achievement=Achievement.objects.get(name=achievement_name))
            except ObjectDoesNotExist:
                pass
            user_activity = Activity.objects.create(user=request.user, image="badges/tree.png",
                                                    name=f"You've earned \"{achievement_name}\" achievement",
                                                    points=points)
            activity_points(request, user_activity.points)
        except IntegrityError:
            pass

@anonymous_prohibited_with_id
# returns user data of the current user logged in to be displayed as a profile card
def profile(request, id):
    profile_user = User.objects.get(id=id)
    user_level = UserLevel.objects.get(user=profile_user)
    current_level_name = user_level.level.name
    user_tier_colour = get_user_tier_colour(profile_user)
    reached_tiers = get_reached_tiers(UserLevel.objects.get(user=profile_user).points)
    try:
        avatar = 'avatar/' + Avatar.objects.get(user=profile_user).file_name
        avatar_path = os.path.join(settings.STATICFILES_DIRS[0], avatar)
        if not os.path.exists(avatar_path):
            avatar = 'avatar/default_avatar.png'
    except Avatar.DoesNotExist:
        avatar = 'avatar/default_avatar.png'
    user_achievements = UserAchievement.objects.filter(user=profile_user)
    user_posts = Post.objects.filter(user=profile_user)
    if reached_tiers:
        user_tier_name, tier_data = reached_tiers.popitem()
    else:
        user_tier_name = ""
    context = {
        'profile_user': profile_user,
        'user_tier_colour': user_tier_colour,
        'user_tier_name': user_tier_name,
        'current_level_name': current_level_name,
        'user_level': user_level,
        'avatar': avatar,
        'user_achievements': user_achievements,
        'user_posts': user_posts,
    }
    return render(request, 'profile.html', context)

@user_prohibited
@anonymous_prohibited
def superuser_dashboard(request):
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            will_be_admin = request.POST.get('will_be_admin', 0)
            if (will_be_admin != 0):
                user.is_staff = True
                user.save()
            return redirect('superuser_dashboard')
    else:
        form = CreateUserForm()

    user_list = User.objects.all().order_by('id')
    paginator = Paginator(user_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, 'superuser_dashboard.html', {'form': form, 'page': page})

# redirects to admin dashboard for admin users, with checks if any object creation has occured e.g category creations
def admin_dashboard(request):
    view = request.GET.get('view', 'Users')
    if (request.user.is_staff == True):
        if request.method == 'POST':
            # IF CREATE USER BUTTON CLICKED
            if 'create_user' in request.POST:
                form = CreateUserForm(request.POST)
                if form.is_valid():
                    user = form.save()
                    if (request.POST.get('will_be_admin') != None):
                        user.is_staff = True
                        user.save()
                    return redirect('admin_dashboard')
                else:
                    messages.info(request, 'Unsuccessful creation of user, please try again ensuring email is valid and passwords match.')
                    return redirect('admin_dashboard')

            # IF CREATE CATEGORY BUTTON CLICKED
            elif 'create_category' in request.POST:
                form = AddCategoryForm(request.POST)
                if form.is_valid():
                    category = form.save()
                    category.is_global = True
                    category.save()
                    return redirect('admin_dashboard')
                else:
                    messages.info(request, 'Unsuccessful creation of category.')
                    return redirect('admin_dashboard')

            # IF CREATE CHALLENGE BUTTON CLICKED
            elif 'create_challenge' in request.POST:
                form = AddChallengeForm(request.POST)
                if form.is_valid():
                    challenge = form.save()
                    return redirect('admin_dashboard')
                else:
                    messages.info(request, 'Unsuccessful creation of challenge')
                    return redirect('admin_dashboard')

            elif 'create_achievement' in request.POST:
                form = AddAchievementForm(request.POST)
                if form.is_valid():
                    achievement = form.save()
                    achievement.badge = "badges/custom.png"
                    achievement.save()
                    return redirect('admin_dashboard')
                else:
                    messages.info(request, 'Unsuccessful creation of achievement')
                    return redirect('admin_dashboard')

            else:
                return redirect('admin_dashboard')

        else:
            # DEFAULT TABLE TO LOAD ON PAGE
            user_list = User.objects.all().order_by('id')
            if not request.user.is_superuser:
                user_list = User.objects.filter(is_staff = False).order_by('id')
            user_paginator = Paginator(user_list, 8)
            user_page_number = request.GET.get('page')
            user_page = user_paginator.get_page(user_page_number)

            category_list = Category.objects.filter(is_global=True).order_by('id')
            category_paginator = Paginator(category_list, 8)
            category_page_number = request.GET.get('page')
            category_page = category_paginator.get_page(category_page_number)

            challenge_list = Challenge.objects.all().order_by('id')
            challenge_paginator = Paginator(challenge_list, 8)
            challenge_page_number = request.GET.get('page')
            challenge_page = challenge_paginator.get_page(challenge_page_number)

            achievement_list = Achievement.objects.all().order_by('id')
            achievement_paginator = Paginator(achievement_list, 8)
            achievement_page_number = request.GET.get('page')
            achievement_page = achievement_paginator.get_page(achievement_page_number)

            user_form = CreateUserForm()
            category_form = AddCategoryForm()
            challenge_form = AddChallengeForm()
            achievement_form = AddAchievementForm()

    else:
        return redirect('landing_page')

    context = {
        'view': view,
        'user_page': user_page,
        'category_page': category_page,
        'challenge_page': challenge_page,
        'achievement_page': achievement_page,
        'user_form': user_form,
        'category_form': category_form,
        'challenge_form': challenge_form,
        'achievement_form': achievement_form}

    return render(request, 'admin_dashboard.html', context)

# returns list of all users for admin dashboard
def user_table(request):
  user_list = User.objects.all().order_by('id')
  if not request.user.is_superuser:
      user_list = User.objects.filter(is_staff = False).order_by('id')
  user_paginator = Paginator(user_list, 8)
  user_page_number = request.GET.get('page')
  user_page = user_paginator.get_page(user_page_number)
  return render(request, 'user_table.html', {'user_page': user_page})

# returns list of all existing categories for admin dashboard
def category_table(request):
  category_list = Category.objects.filter(is_global=True).order_by('id')
  category_paginator = Paginator(category_list, 8)
  category_page_number = request.GET.get('page')
  category_page = category_paginator.get_page(category_page_number)
  return render(request, 'category_table.html', {'category_page': category_page})

# returns list of all existing challenges available for admin dashboard
def challenge_table(request):
  challenge_list = Challenge.objects.all().order_by('id')
  challenge_paginator = Paginator(challenge_list, 8)
  challenge_page_number = request.GET.get('page')
  challenge_page = challenge_paginator.get_page(challenge_page_number)
  return render(request, 'challenge_table.html', {'challenge_page': challenge_page})

# returns list of all existing achievements available for admin dashboard
def achievement_table(request):
  achievement_list = Achievement.objects.all().order_by('id')
  achievement_paginator = Paginator(achievement_list, 8)
  achievement_page_number = request.GET.get('page')
  achievement_page = achievement_paginator.get_page(achievement_page_number)
  return render(request, 'achievement_table.html', {'achievement_page': achievement_page})

# admin deletion function which will determine what object was selected to be deleted and deletes them from the database
def delete(request):
    if request.method == "POST":
        if 'user_pk' in request.POST:
            try:
                user_pk = request.POST['user_pk']
                u = User.objects.get(pk = user_pk)
                u.delete()
                return redirect('admin_dashboard')
            except User.DoesNotExist:
                return redirect('admin_dashboard')

        elif 'category_pk' in request.POST:
            try:
                category_pk = request.POST['category_pk']
                c = Category.objects.get(pk = category_pk)
                c.delete()
                return redirect('admin_dashboard')
            except Category.DoesNotExist:
                return redirect('admin_dashboard')

        elif 'challenge_pk' in request.POST:
            try:
                challenge_pk = request.POST['challenge_pk']
                ch = Challenge.objects.get(pk = challenge_pk)
                ch.delete()
                return redirect('admin_dashboard')
            except Challenge.DoesNotExist:
                return redirect('admin_dashboard')

        elif 'achievement_pk' in request.POST:
            try:
                achievement_pk = request.POST['achievement_pk']
                a = Achievement.objects.get(pk = achievement_pk)
                a.delete()
                return redirect('admin_dashboard')
            except Achievement.DoesNotExist:
                return redirect('admin_dashboard')

        else:
            return redirect('admin_dashboard')
    else:
        return redirect('admin_dashboard')

#  promotes a standard user to admin by changing is_staff to True
def user_promote(request):
    if request.method == "POST":
        try:
            if 'user_pk' in request.POST:
                user_pk = request.POST['user_pk']
                u = User.objects.get(pk = user_pk)
                u.is_staff = True
                u.save()
                return redirect('admin_dashboard')
            else:
                return redirect('admin_dashboard')

        except User.DoesNotExist:
            return redirect('admin_dashboard')
    else:
        return redirect('admin_dashboard')

# demotes an admin to standard user by changing is_staff to False
def user_demote(request):
    if request.method == "POST":
        try:
            if 'user_pk' in request.POST:
                user_pk = request.POST['user_pk']
                u = User.objects.get(pk = user_pk)
                u.is_staff = False
                u.save()
                return redirect('admin_dashboard')
            else:
                return redirect('admin_dashboard')

        except User.DoesNotExist:
            return redirect('admin_dashboard')
    else:
        return redirect('admin_dashboard')
