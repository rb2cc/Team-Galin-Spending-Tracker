
from .forms import SignUpForm, LogInForm, EditUserForm, CreateUserForm
from django.contrib.auth.forms import UserChangeForm
from .models import User

from .forms import SignUpForm, LogInForm, ExpenditureForm, AddCategoryForm, AddChallengeForm, AddAchievementForm
from .models import User, Category, Expenditure, Challenge, UserChallenge, Achievement, UserAchievement, Level, UserLevel

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import user_passes_test, login_required
from django.urls import reverse, reverse_lazy
from django.views import generic

from datetime import date, timedelta, datetime
from django.utils import timezone
from django.utils.datastructures import MultiValueDictKeyError
from django.db.models import Q
from django.db import IntegrityError
from math import floor
from urllib.parse import urlencode, unquote
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect


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
                if user.is_superuser or user.is_staff == True:
                    return redirect('admin_dashboard')
                else:
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
                for x in global_categories:
                    tempName = x.name
                    tempLimit = x.week_limit
                    tempCategory = Category.objects.create(name=tempName, week_limit=tempLimit)
                    user.available_categories.add(tempCategory)
                login(request, user)
                user_achievement = UserAchievement.objects.create(user=request.user, achievement = Achievement.objects.get(name="New user"))
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
            return redirect('landing_page')
    else:


        form = ExpenditureForm(r=request)
    objectList = Expenditure.objects.filter(user=request.user, is_binned=False)

    '''Data for list display'''
    spendingList = objectList.order_by('-date_created')[0:19]

    if spendingList.count() == 1:
        try:
            user_achievement = UserAchievement.objects.create(user=request.user, achievement=Achievement.objects.get(name="First expenditure"))
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
        'is_superuser': request.user.is_superuser,
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
    return render(request, 'change_password_success.html')

class UserEditView(generic.UpdateView):
    form_class = EditUserForm
    template_name = 'edit_user.html'
    success_url = reverse_lazy('landing_page')

    def get_object(self):
        return self.request.user

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
            return redirect('category_list')
    else:
        form = AddCategoryForm()
    categoryList = Category.objects.filter(users__id=user_id).order_by('name')
    if categoryList.count() == 1:
        try:
            user_achievement = UserAchievement.objects.create(user=request.user, achievement=Achievement.objects.get(name="Budget boss"))
        except IntegrityError:
            pass
    return render(request, 'category_list.html', {'categories':categoryList, 'form':form})

def remove_category(request, id):
    category = Category.objects.get(id = id)
    if category.is_global:
        request.user.available_categories.remove(category)
    else:
        category.delete()
    return redirect('category_list')


def edit_category(request, id):
    current_user = request.user
    category = Category.objects.get(id = id)
    if request.method == "POST":
        form = AddCategoryForm(request.POST, instance = category)
        if form.is_valid():
            category = form.save(commit=False)
            category.save()
            return redirect('category_list')
    else:
        form = AddCategoryForm(instance=category)
    return render(request, 'edit_category.html', {'form' : form})

def forum_home(request):
    return render(request, 'forum/forum_home.html')


def posts(request):
    return render(request, 'forum/posts.html')


def detail(request):
    return render(request, 'forum/detail.html')

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
            # Challenge already completed, do nothing
            return

        # Set the date completed to the current time
        user_challenge.date_completed = timezone.now()
        user_challenge.save()

        user_challenges_count = UserChallenge.objects.filter(user=request.user).count()
        if user_challenges_count == 1:
            user_achievement = UserAchievement.objects.create(user=request.user, achievement=Achievement.objects.get(name="Wise spender"))
        elif user_challenges_count == 10:
            user_achievement = UserAchievement.objects.create(user=request.user, achievement=Achievement.objects.get(name="Superstar"))

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

def update_user_level(user):
    # Get the user's total points
    user_level = UserLevel.objects.get(user=user)
    total_points = user_level.points

    # Calculate the user's current level
    try:
        current_level = Level.objects.get(name = f"Level {floor(total_points / 100) + 1}")
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
        	new_level.save()

        current_level = Level.objects.get(name = f"Level {floor(total_points / 100) + 1}")
        user_level.level = current_level
        user_level.save()

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
        'facebook': 'https://www.facebook.com/dialog/share?' + urlencode(facebook_params),
        'twitter': 'https://twitter.com/share?' + urlencode(twitter_params),
    }

    if isinstance(user_object, UserAchievement):
        return render(request, 'share.html', {'name': name, 'description': description, 'share_urls': share_urls, 'type': 'achievement'})
    elif isinstance(user_object, UserChallenge):
        return render(request, 'share.html', {'name': name, 'description': description, 'share_urls': share_urls, 'type': 'challenge'})

def handle_share(request):
    share_url = unquote(request.GET.get('share_url'))
    try:
        user_achievement = UserAchievement.objects.create(user=request.user, achievement=Achievement.objects.get(name="First share"))
    except IntegrityError:
        pass
    return redirect(share_url)

@login_required
def my_achievements(request):
    user_achievements = UserAchievement.objects.filter(user=request.user)
    return render(request, 'my_achievements.html', {'user_achievements': user_achievements})


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

    user_list = User.objects.all()
    paginator = Paginator(user_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, 'superuser_dashboard.html', {'form': form, 'page': page})

def admin_dashboard(request):
    if (request.user.is_staff == False) and (request.user.is_superuser == False):
        return redirect('landing_page')
    else:
        if request.method == 'POST':
            # IF CREATE USER BUTTON CLICKED
            if 'create_user' in request.POST:
                form = CreateUserForm(request.POST)
                if form.is_valid():
                    user = form.save()
                    return redirect('admin_dashboard')

            # IF CREATE CATEGORY BUTTON CLICKED
            if 'create_category' in request.POST:
                form = AddCategoryForm(request.POST)
                if form.is_valid():
                    category = form.save()
                    category.is_global = True
                    category.save()
                    return redirect('admin_dashboard')

            # IF CREATE CHALLENGE BUTTON CLICKED
            if 'create_challenge' in request.POST:
                form = AddChallengeForm(request.POST)
                if form.is_valid():
                    challenge = form.save()
                    return redirect('admin_dashboard')

            if 'create_achievement' in request.POST:
                form = AddAchievementForm(request.POST)
                if form.is_valid():
                    achievement = form.save()
                    achievement.badge = "badges/custom.png"
                    achievement.save()
                    return redirect('admin_dashboard')

        else:
            # DEFAULT TABLE TO LOAD ON PAGE
            user_table = 'user_table.html'
            user_list = User.objects.all()
            user_paginator = Paginator(user_list, 5)
            user_page_number = request.GET.get('page')
            user_page = user_paginator.get_page(user_page_number)

            user_form = CreateUserForm()
            category_form = AddCategoryForm()
            challenge_form = AddChallengeForm()
            achievement_form = AddAchievementForm()

        return render(request, 'admin_dashboard.html', {'user_page': user_page,'user_table': user_table,
        'user_form': user_form, 'category_form': category_form, 'challenge_form': challenge_form, 'achievement_form': achievement_form})

def user_table(request):
  user_list = User.objects.all()
  user_paginator = Paginator(user_list, 5)
  user_page_number = request.GET.get('page')
  user_page = user_paginator.get_page(user_page_number)
  return render(request, 'user_table.html', {'user_page': user_page})

def category_table(request):
  category_list = Category.objects.all()
  category_paginator = Paginator(category_list, 5)
  category_page_number = request.GET.get('page')
  category_page = category_paginator.get_page(category_page_number)
  return render(request, 'category_table.html', {'category_page': category_page})

def challenge_table(request):
  challenge_list = Challenge.objects.all()
  challenge_paginator = Paginator(challenge_list, 5)
  challenge_page_number = request.GET.get('page')
  challenge_page = challenge_paginator.get_page(challenge_page_number)
  return render(request, 'challenge_table.html', {'challenge_page': challenge_page})

def achievement_table(request):
  achievement_list = Achievement.objects.all()
  achievement_paginator = Paginator(achievement_list, 5)
  achievement_page_number = request.GET.get('page')
  achievement_page = achievement_paginator.get_page(achievement_page_number)
  return render(request, 'achievement_table.html', {'achievement_page': achievement_page})


def user_delete(request):
    if request.method == "POST":
        try:
            user_pk = request.POST['user_pk']
            u = User.objects.get(pk = user_pk)
            u.delete()
            return redirect('superuser_dashboard')

        except User.DoesNotExist:
            return redirect('superuser_dashboard')

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

        else:
            return redirect('admin_dashboard')


def user_promote(request):
    if request.method == "POST":
        try:
            if 'user_pk' in request.POST:
                user_pk = request.POST['user_pk']
                u = User.objects.get(pk = user_pk)
                if u.is_staff == True:
                    messages.info(request, 'This is a test')
                else:
                    u.is_staff = True
                    u.save()
                return redirect('admin_dashboard')
            else:
                return redirect('sadmin_dashboard')

        except User.DoesNotExist:
            return redirect('admin_dashboard')

def user_demote(request):
    if request.method == "POST":
        try:
            if 'user_pk' in request.POST:
                user_pk = request.POST['user_pk']
                u = User.objects.get(pk = user_pk)
                if u.is_staff == False:
                    messages.info(request, 'This is a test')
                else:
                    u.is_staff = False
                    u.save()
                return redirect('admin_dashboard')
            else:
                return redirect('admin_dashboard')

        except User.DoesNotExist:
            return redirect('admin_dashboard')


# def display_expenditures(request):
#     expenditures = Expenditure.objects.all()
#     return render(request, 'expenditure_list.html', {'expenditures':expenditures})
