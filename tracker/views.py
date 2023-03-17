from .forms import SignUpForm, LogInForm, EditUserForm, ReportForm, PostForm
from django.contrib.auth.forms import UserChangeForm
from .models import User, Category, Expenditure, Challenge, UserChallenge, Achievement, UserAchievement, Level, UserLevel, Activity, Post, Forum_Category, Comment, Reply, Avatar
from .forms import SignUpForm, LogInForm, ExpenditureForm, AddCategoryForm, EditOverallForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import user_passes_test, login_required
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.views.generic import TemplateView
from datetime import date, timedelta, datetime
from django.utils import timezone
from django.utils.datastructures import MultiValueDictKeyError
from django.db.models import Q
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

# Create your views here.

def home(request):
    if request.method == 'POST':
        form = LogInForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('landing_page')
        messages.add_message(request, messages.ERROR, "The credentials provided were invalid")
    form = LogInForm()
    return render(request, 'home.html', {'form': form})


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
                Activity.objects.create(user=request.user, image = "images/user.png", name = "You've created an account on Galin's Spending Tracker")
                Activity.objects.create(user=request.user, image = "badges/new_user.png", name = "You've earned \"New user\" achievement")
                overall = Category.objects.create(name="Overall", week_limit=overall_count, is_overall = True)
                user.available_categories.add(overall)
                return redirect('landing_page')
            else:
                messages.add_message(request, messages.ERROR, "This email has already been registered")          
    else:
        form = SignUpForm()
    return render(request, 'sign_up.html', {'form': form})


def log_out(request):
    logout(request)
    return redirect('home')


def user_test(user):
    return user.is_anonymous == False


@user_passes_test(user_test, login_url='log_out')
def landing_page(request):
    if request.method == 'POST':
        form=ExpenditureForm(request.POST, request.FILES, r=request)
        if form.is_valid():
            expenditure = form.save(commit=False)
            expenditure.user = request.user
            expenditure.save()
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


def getCumulativeExpenseList(objectList, dailyExpenseList):
    cumulativeExpenseList = []
    cumulativeExpense = 0
    for x in dailyExpenseList:
        cumulativeExpense += x
        cumulativeExpenseList.append(cumulativeExpense)
    return cumulativeExpenseList


def getAllList(objectList, num, request):
    first = getCategoryAndExpenseList(objectList, request)
    cat = first[0]
    exp = first[1]
    second = getDateListAndDailyExpenseList(objectList, num)
    dat = second[0]
    dai = second[1]
    cum = getCumulativeExpenseList(objectList, dai)
    return cat, exp, dat, dai, cum

def change_password_success(request):
    Activity.objects.create(user=request.user, image = "images/edit.png", name = "You've changed your password")
    return render(request, 'change_password_success.html')

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

    def update_user(request):
        form = EditUserForm(instance=request.user)
        if (request.method) == "POST":
            form = EditUserForm(request.POST, instance=request.user)
            form.save()
            return render(request, 'edit_user.html')
        return render(request, 'edit_user.html')

def category_list(request):
    user_id = request.user.id
    if request.method == 'POST':
        form=AddCategoryForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save(commit=False)
            category.save()
            request.user.available_categories.add(category)
            try:
                try:
                    UserAchievement.objects.create(user=request.user, achievement=Achievement.objects.get(name="Budget boss"))
                except ObjectDoesNotExist:
                    pass
                user_activity = Activity.objects.create(user=request.user, image = "badges/budget_boss.png", name = "You've earned \"Budget boss\" achievement", points = 15)
                activity_points(request, user_activity.points)
            except IntegrityError:
                pass
            user_activity_name = f'You\'ve added \"{category.name}\" category with {category.week_limit} week limit'
            user_activity = Activity.objects.create(user=request.user, image = "images/category.png", name = user_activity_name, points = 15)
            activity_points(request, user_activity.points)
            overall = Category.objects.filter(is_overall = True).get(users__id=request.user.id)
            overall.week_limit += category.week_limit
            overall.save(force_update = True)
            return redirect('category_list')
    else:
        form = AddCategoryForm()
    categoryList = Category.objects.filter(users__id=user_id).filter(is_overall=False).order_by('name')
    overall = Category.objects.filter(users__id=user_id).get(is_overall=True)
    return render(request, 'category_list.html', {'categories':categoryList, 'form':form, 'overall':overall})

def bin_category(request, id):
    category = Category.objects.get(id = id)
    category_name = category.name
    diff = category.week_limit
    if category.is_global:
        request.user.available_categories.remove(category)
    else:
        # category.delete()
        category.is_binned = True
        category.save()
    expenditures_of_category=Expenditure.objects.filter(is_binned=False,category=category)
    for expenditure in expenditures_of_category:
        expenditure.is_binned = True
        expenditure.save()
    Activity.objects.create(user=request.user, image = "images/delete.png", name = f'You\'ve deleted \"{category_name}\" category')
    overall = Category.objects.filter(is_overall = True).get(users__id=request.user.id)
    overall.week_limit -= diff
    overall.save(force_update = True)
    return redirect('category_list')

def edit_category(request, id):
    current_user = request.user
    category = Category.objects.get(id = id)
    category_name = category.name
    category_week_limit = category.week_limit
    before_limit = category.week_limit
    if request.method == "POST":
        if category.is_overall==False:
            form = AddCategoryForm(request.POST, instance = category)
            if form.is_valid():
                category = form.save(commit=False)
                category.save()
                if (category.name != category_name):
                    activity_name = f'You\'ve changed \"{category_name}\" category name to \"{category.name}\"'
                    Activity.objects.create(user=request.user, image = "images/edit.png", name = activity_name)
                if (category.week_limit != category_week_limit):
                    activity_name = f'You\'ve changed \"{category.name}\" category week limit from {category_week_limit} to {category.week_limit}'
                    Activity.objects.create(user=request.user, image = "images/edit.png", name = activity_name)
                diff = before_limit - category.week_limit       
                overall = Category.objects.filter(is_overall = True).get(users__id=current_user.id)
                overall.week_limit -= diff
                overall.save(force_update = True)
                return redirect('category_list')
        else:
            form = EditOverallForm(request.POST, instance = category, user = current_user)
            if form.is_valid():
                category = form.save(commit=False)
                category.save()
                if (category.week_limit != category_week_limit):
                    activity_name = f'You\'ve changed \"{category.name}\" category week limit from {category_week_limit} to {category.week_limit}'
                    Activity.objects.create(user=request.user, image = "images/edit.png", name = activity_name)
                return redirect('category_list')
    else:
        if category.is_overall==False:
            form = AddCategoryForm(instance=category)
        else:
            form = EditOverallForm(instance=category, user = current_user)
    return render(request, 'edit_category.html', {'form' : form})

#Gets all expenditures under the filter of being binned
def binned_category_list(request):
    binned_list = Category.objects.filter(users__id=request.user.id).filter(is_overall=False, is_binned=True).order_by('name')
    return render(request, 'category_bin.html', {'binned_categories': binned_list})

#Gets id field of the selected expenditure recover button and changes the is_binned field from true to false
def recover_category(request):
    if request.method == "POST":
        try:
            category_pk = request.POST['radio_pk']
            category = Category.objects.get(pk=category_pk)
            category.is_binned = False
            category.save()
            overall = overall = Category.objects.filter(is_overall = True).get(users__id=request.user.id)
            overall.week_limit += category.week_limit
            overall.save(force_update = True)
            expenditures_of_category=Expenditure.objects.filter(is_binned=True, category=category)
            for expenditure in expenditures_of_category:
                expenditure.is_binned = False
                expenditure.save()
            # Activity.objects.create(user=request.user, image = "images/recover.png", name = f'You\'ve recovered \"{expenditure.title}\" expenditure from the bin')
            return redirect('category_bin')
        except Expenditure.DoesNotExist:
            return redirect('category_bin')
        except MultiValueDictKeyError:
            return redirect('category_bin')

#Gets id field of the selected expenditure delete button and deletes the object from the database
def delete_category(request):
    if request.method == "POST":
        try:
            category_pk = request.POST['radio_pk']
            category = Category.objects.get(pk=category_pk)
            category.delete()
            all_expenditures=Expenditure.objects.filter(is_binned=False)
            for expenditure in all_expenditures:
                expenditure.category = None
                expenditure.is_binned = True
                expenditure.save()
            # Activity.objects.create(user=request.user, image = "images/delete.png", name = f'You\'ve deleted \"{expenditure_title}\" expenditure')
            return redirect('category_bin')
        except Expenditure.DoesNotExist:
            return redirect('category_bin')
        except MultiValueDictKeyError:
            return redirect('category_bin')

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

def posts(request, slug):
    category = get_object_or_404(Forum_Category, slug=slug)
    posts = Post.objects.filter(approved=True, forum_categories=category)
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

# @login_required(login_url=reverse_lazy("login"))
def detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    posts = Post.objects.all()
    author = request.user
    points = {}
    avatars = {}
    tier_colours = {}
    user_levels = {}
    user_tier_names = {}

    if "comment-form" in request.POST:
        comment = request.POST.get("comment")
        media = request.FILES.get("media")
        new_comment, created = Comment.objects.get_or_create(user=author, content=comment, media=media)
        post.comments.add(new_comment.id)

    if "reply-form" in request.POST:
        reply = request.POST.get("reply")
        media = request.FILES.get("media")
        comment_id = request.POST.get("comment-id")
        comment_obj = Comment.objects.get(id=comment_id)
        new_reply, created = Reply.objects.get_or_create(user=author, content=reply, media=media)
        comment_obj.replies.add(new_reply.id)

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

@login_required
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
            return redirect("forum_home")
    context.update({
        "form": form,
        "title": "Create New Post"
    })
    return render(request, "forum/create_post.html", context)

def delete_post(request, id):
    try:
        post = Post.objects.get(id = id)
        post.delete()
    except Post.DoesNotExist:
        pass
    return redirect('forum_home')

def edit_post(request, id):
    try:
        post = Post.objects.get(id=id)
        if request.method == "POST":
            form = PostForm(request.POST, instance=post)
            if form.is_valid():
                post = form.save(commit=False)
                post.save()
                form.save_m2m()
                return redirect('forum_home')
        else:
            form = PostForm(instance=post)
    except Post.DoesNotExist:
        return redirect('forum_home')
    return render(request, 'forum/edit_post.html', {'form' : form})

def delete_comment(request, id):
    try:
        comment = Comment.objects.get(id=id)
        post = Post.objects.get(comments=comment)
        post.comments.remove(comment)
        post_slug = post.slug
        comment.delete()
        return redirect(reverse('detail', args=[post_slug]))
    except Comment.DoesNotExist:
        pass
    return redirect('forum_home')

def edit_comment(request, id):
    return

def delete_reply(request, id):
    try:
        reply = Reply.objects.get(id=id)
        comment = Comment.objects.get(replies=reply)
        comment.replies.remove(reply)
        reply.delete()
        post = Post.objects.get(comments=comment)
        post_slug = post.slug
        return redirect(reverse('detail', args=[post_slug]))
    except Reply.DoesNotExist:
        pass
    return redirect('forum_home')

def edit_reply(request, id):
    return

def latest_posts(request):
    posts = Post.objects.all().filter(approved=True)[:10]
    context = {
        "posts": posts,
        "title": "Latest 10 Posts"
    }
    return render(request, "forum/latest_posts.html", context)

def search_result(request):
    query = request.GET.get('q')
    results = Post.objects.filter(title__icontains=query)

    paginator = Paginator(results, 5)
    page = request.GET.get('page')
    objects = paginator.get_page(page)

    context = {
        'query': query,
        'objects': objects,
    }
    return render(request, 'forum/search.html', context)

def challenge_list(request):
    challenges = Challenge.objects.all()
    return render(request, 'challenge_list.html', {'challenges': challenges})

def achievement_list(request):
    achievements = Achievement.objects.all()
    return render(request, 'achievement_list.html', {'achievements': achievements})

def challenge_details(request, id):
    challenge = Challenge.objects.get(id=id)
    return render(request, 'challenge_details.html', {'challenge': challenge})

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

@login_required
def my_challenges(request):
    user_challenges = UserChallenge.objects.filter(user=request.user)
    return render(request, 'my_challenges.html', {'user_challenges': user_challenges})

def complete_challenge(request, challenge_id):
    user_challenge = UserChallenge.objects.get(user=request.user, challenge_id=challenge_id)
    if user_challenge is not None:
        if user_challenge.date_completed is not None:
            return

        user_challenge.date_completed = timezone.now()
        user_challenge.save()

        user_challenges_count = UserChallenge.objects.filter(user=request.user).count()
        try:
            if user_challenges_count == 1:
                UserAchievement.objects.create(user=request.user, achievement=Achievement.objects.get(name="Wise spender"))
                user_activity = Activity.objects.create(user=request.user, image = "badges/wise_spender.png", name = "You've earned \"Wise spender\" achievement", points = 15)
                activity_points(request, user_activity.points)
            elif user_challenges_count == 10:
                UserAchievement.objects.create(user=request.user, achievement=Achievement.objects.get(name="Superstar"))
                user_activity = Activity.objects.create(user=request.user, image = "badges/super_star.png", name = "You've earned \"Superstar\" achievement", points = 150)
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

def activity_points(request, points):
    try:
        user_level = UserLevel.objects.get(user=request.user)
        user_level.points += points
        user_level.save()
        update_user_level(request.user)
    except ObjectDoesNotExist:
        pass

def update_user_level(user):
    user_level = UserLevel.objects.get(user=user)
    total_points = user_level.points

    try:
        current_level = Level.objects.get(name = f"Level {floor(total_points / 100) + 1}")
        if (user_level.level.id < current_level.id):
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

def share_avatar(request):
    svg = "avatar"
    name = "My avatar"
    description = "Avatar created in Galin's Spending Tracker"
    url = request.build_absolute_uri(reverse('my_avatar'))
    text = "Here is my avatar created in Galin's Spending Tracker"
    return share(request, svg, name, description, url, text)

def share_challenge(request, id):
    user_challenge = UserChallenge.objects.get(id=id)
    name = user_challenge.challenge.name
    description = user_challenge.challenge.description
    url = request.build_absolute_uri(reverse('challenge_details', args=[str(user_challenge.challenge.id)]))
    text = f"I'm doing the \"{name}\" challenge on Galin's Spending Tracker"
    return share(request, user_challenge, name, description, url, text)

def share_achievement(request, id):
    user_achievement = UserAchievement.objects.get(id=id)
    name = user_achievement.achievement.name
    description = user_achievement.achievement.description
    url = request.build_absolute_uri(reverse('achievement_list'))
    text = f"I've earned the \"{name}\" achievement on Galin's Spending Tracker"
    return share(request, user_achievement, name, description, url, text)

def share_post(request, id):
    post = Post.objects.get(id=id)
    name = post.title
    description = "Forum post on Galin's Spending Tracker"
    url = request.build_absolute_uri(post.get_url())
    text = f"Check out my \"{name}\" post on Galin's Spending Tracker"
    return share(request, post, name, description, url, text)

def share_comment(request, id):
    return

def share_reply(request, id):
    return

def share(request, user_object, name, description, url, text):
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
        'Facebook': 'https://www.facebook.com/dialog/share?' + urlencode(facebook_params),
        'Twitter': 'https://twitter.com/share?' + urlencode(twitter_params),
        'Forum': request.build_absolute_uri(reverse('create_post'))
    }

    if isinstance(user_object, UserAchievement):
        return render(request, 'share.html', {'name': name, 'description': description, 'share_urls': share_urls, 'type': 'achievement'})
    elif isinstance(user_object, UserChallenge):
        return render(request, 'share.html', {'name': name, 'description': description, 'share_urls': share_urls, 'type': 'challenge'})
    elif isinstance(user_object, str):
        user_tier_colour = get_user_tier_colour(request.user)
        try:
            avatar = 'avatar/' + Avatar.objects.get(user=request.user).file_name
            avatar_path = os.path.join(settings.STATICFILES_DIRS[0], avatar)
            if not os.path.exists(avatar_path):
                avatar = 'avatar/default_avatar.png'
        except Avatar.DoesNotExist:
            avatar = 'avatar/default_avatar.png'
        return render(request, 'share.html', {'name': name, 'description': description, 'share_urls': share_urls, 'type': 'avatar', 'user_tier_colour': user_tier_colour, 'avatar': avatar})
    elif isinstance(user_object, Post):
        media = user_object.media
        return render(request, 'share.html', {'name': name, 'description': description, 'share_urls': share_urls, 'type': 'post', 'media': media})

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

@login_required
def my_achievements(request):
    user_achievements = UserAchievement.objects.filter(user=request.user)
    return render(request, 'my_achievements.html', {'user_achievements': user_achievements})

@login_required
def my_activity(request):
    num_items = request.GET.get('num_items')
    if num_items == 'all':
        user_activity = Activity.objects.filter(user=request.user).order_by('-time')
    else:
        user_activity = Activity.objects.filter(user=request.user).order_by('-time')[:int(num_items)]
    return render(request, 'my_activity.html', {'user_activity': user_activity})

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

    return render(request, 'my_avatar.html', {'components': components, 'colours': colours, 'locked_items': locked_items, 'tier_info': tier_info, 'user_tier_colour': user_tier_colour})

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

def get_svg_paths_for_component(category, component):
    file_name = component + '.svg'
    item_path = os.path.join(settings.STATICFILES_DIRS[0], 'avatar', category, file_name)
    svg = open(item_path, 'r').read()
    path_tags = re.findall(r'<path.*?/>', svg)
    return ''.join(path_tags)

def get_avatar_colours():
    colours = {'skin': ['#694d3d', '#ae5d29', '#d08b5b', '#edb98a', '#ffdbb4'],
        'accessories': ['#78e185', '#8fa7df', '#9ddadb', '#e279c7', '#e78276', '#fdea6b', '#ffcf77'],
        'shirt': ['#78e185', '#8fa7df', '#9ddadb', '#e279c7', '#e78276', '#fdea6b', '#ffcf77'],
        'hair': ['#aa8866', '#debe99', '#241c11', '#4f1a00', '#9a3300'],
        'background': ['#b6e3f4', '#c0aede', '#d1d4f9', '#ffd5dc', '#ffdfbf']}
    return colours

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
def check_forum_instance(type, value):
    if isinstance(value, Post):
        type = "post"
    elif isinstance(value, Comment):
        type = "comment"
    elif isinstance(value, Reply):
        type = "reply"
    return type

def create_forum_avatar(request, id):
    query_dict = request.GET.copy()
    query_dict['user'] = id
    request.GET = query_dict
    return create_avatar(request)

def report(request):
    user = request.user
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
        else:
            start_date = None
            end_date = None
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

@csrf_exempt
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
            user_activity = Activity.objects.create(user=request.user, image="badges/custom.png",
                                                    name=f"You've earned \"{achievement_name}\" achievement",
                                                    points=points)
            activity_points(request, user_activity.points)
        except IntegrityError:
            pass

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