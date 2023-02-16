
from .forms import SignUpForm, LogInForm, EditUserForm
from django.contrib.auth.forms import UserChangeForm
from .models import User
from .forms import SignUpForm, LogInForm, ExpenditureForm, AddCategoryForm
from .models import User, Category, Expenditure, Challenge, UserChallenge, Achievement, UserAchievement, Level, UserLevel, Activity
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import user_passes_test, login_required
from django.urls import reverse, reverse_lazy
from django.views import generic
from datetime import date, timedelta, datetime
from django.utils import timezone
from django.db import IntegrityError
from math import floor
from urllib.parse import urlencode, unquote


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
                for x in global_categories:
                    tempName = x.name
                    tempLimit = x.week_limit
                    tempCategory = Category.objects.create(name=tempName, week_limit=tempLimit)
                    user.available_categories.add(tempCategory)
                login(request, user)
                user_achievement = UserAchievement.objects.create(user=request.user, achievement = Achievement.objects.get(name="New user"))
                user_activity = Activity.objects.create(user=request.user, image = "images/user.png", name = "You've created an account on Galin's Spending Tracker")
                user_activity = Activity.objects.create(user=request.user, image = "badges/new_user.png", name = "You've earned \"New user\" achievement")
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
    objectList = Expenditure.objects.filter(user=request.user)

    '''Data for list display'''
    spendingList = objectList.order_by('-date_created')[0:19]

    if spendingList.count() == 1:
        try:
            user_achievement = UserAchievement.objects.create(user=request.user, achievement=Achievement.objects.get(name="First expenditure"))
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
    })


def getCategoryAndExpenseList(objectList, request):
    categoryList = []
    expenseList = []
    for x in request.user.available_categories.all():
        tempList = objectList.filter(category=x)
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
    for x in objectList.order_by('date_created'):
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
    user_activity = Activity.objects.create(user=request.user, image = "images/edit.png", name = "You've changed your password")
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
            user_activity = Activity.objects.create(user=self.request.user, image = "images/edit.png", name = activity_name)
        if old_first_name != user.first_name:
            activity_name = f'You\'ve changed your first name from {old_first_name} to {user.first_name}'
            user_activity = Activity.objects.create(user=self.request.user, image = "images/edit.png", name = activity_name)
        if old_last_name != user.last_name:
            activity_name = f'You\'ve changed your last name from {old_last_name} to {user.last_name}'
            user_activity = Activity.objects.create(user=self.request.user, image = "images/edit.png", name = activity_name)

        return super().form_valid(form)

    def update_user(request):
        form = EditUserForm(instance=request.user)
        if (request.method) == "POST":
            form = EditUserForm(request.POST, instance=request.user)
            form.save()
            return render(request, 'edit_user.html')
        return render(request, 'edit_user.html')


def expenditure_list(request):
    spendingList = Expenditure.objects.filter(user=request.user).order_by('-date_created')
    return render(request, 'expenditure_list.html', {'spendings': spendingList})


def category_list(request):
    user_id = request.user.id
    if request.method == 'POST':
        form=AddCategoryForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save(commit=False)
            category.save()
            request.user.available_categories.add(category)
            user_activity_name = f'You\'ve added \"{category.name}\" category with {category.week_limit} week limit'
            user_activity = Activity.objects.create(user=request.user, image = "images/category.png", name = user_activity_name, points = 15)
            activity_points(request, user_activity.points)
            return redirect('category_list')
    else:
        form = AddCategoryForm()
    categoryList = Category.objects.filter(users__id=user_id).order_by('name')
    if categoryList.count() == 1:
        try:
            user_achievement = UserAchievement.objects.create(user=request.user, achievement=Achievement.objects.get(name="Budget boss"))
            user_activity = Activity.objects.create(user=request.user, image = "badges/budget_boss.png", name = "You've earned \"Budget boss\" achievement", points = 15)
            activity_points(request, user_activity.points)
        except IntegrityError:
            pass
    return render(request, 'category_list.html', {'categories':categoryList, 'form':form})

def remove_category(request, id):
    category = Category.objects.get(id = id)
    category_name = category.name
    if category.is_global:
        request.user.available_categories.remove(category)
    else:
        category.delete()
    user_activity = Activity.objects.create(user=request.user, image = "images/delete.png", name = f'You\'ve deleted \"{category_name}\" category')
    return redirect('category_list')

def edit_category(request, id):
    current_user = request.user
    category = Category.objects.get(id = id)
    category_name = category.name
    category_week_limit = category.week_limit
    if request.method == "POST":
        form = AddCategoryForm(request.POST, instance = category)
        if form.is_valid():
            category = form.save(commit=False)
            category.save()
            if (category.name != category_name):
                activity_name = f'You\'ve changed \"{category_name}\" category name to \"{category.name}\"'
                user_activity = Activity.objects.create(user=request.user, image = "images/edit.png", name = activity_name)
            if (category.week_limit != category_week_limit):
                activity_name = f'You\'ve changed \"{category.name}\" category week limit from {category_week_limit} to {category.week_limit}'
                user_activity = Activity.objects.create(user=request.user, image = "images/edit.png", name = activity_name)
            return redirect('category_list')
    else:
        form = AddCategoryForm(instance=category)
    return render(request, 'edit_category.html', {'form' : form})
    
# def display_expenditures(request):
#     expenditures = Expenditure.objects.all()
#     return render(request, 'expenditure_list.html', {'expenditures':expenditures})


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
            # Challenge already completed, do nothing
            return

        # Set the date completed to the current time
        user_challenge.date_completed = timezone.now()
        user_challenge.save()

        user_challenges_count = UserChallenge.objects.filter(user=request.user).count()
        if user_challenges_count == 1:
            user_achievement = UserAchievement.objects.create(user=request.user, achievement=Achievement.objects.get(name="Wise spender"))
            user_activity = Activity.objects.create(user=request.user, image = "badges/wise_spender.png", name = "You've earned \"Wise spender\" achievement", points = 15)
            activity_points(request, user_activity.points)
        elif user_challenges_count == 10:
            user_achievement = UserAchievement.objects.create(user=request.user, achievement=Achievement.objects.get(name="Superstar"))
            user_activity = Activity.objects.create(user=request.user, image = "badges/super_star.png", name = "You've earned \"Superstar\" achievement", points = 150)
            activity_points(request, user_activity.points)

        user_activity = Activity.objects.create(user=request.user, image = "images/completed.png", name = f'You\'ve completed \"{user_challenge.challenge.name}\" challenge', points = user_challenge.challenge.points)

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
    user_level = UserLevel.objects.get(user=request.user)
    user_level.points += points
    user_level.save()
    update_user_level(request.user)

def update_user_level(user):
    # Get the user's total points
    user_level = UserLevel.objects.get(user=user)
    total_points = user_level.points

    # Calculate the user's current level
    try:
        current_level = Level.objects.get(name = f"Level {floor(total_points / 100) + 1}")
        if (user_level.level.id < current_level.id):
            user_activity = Activity.objects.create(user=user, image = "images/level_up.png", name = f'You\'ve leveled up to {current_level.name}')
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
        	    user_activity = Activity.objects.create(user=user, image = "images/level_up.png", name = f'You\'ve leveled up to {new_level.name}')
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
        'Facebook': 'https://www.facebook.com/dialog/share?' + urlencode(facebook_params),
        'Twitter': 'https://twitter.com/share?' + urlencode(twitter_params),
    }

    if isinstance(user_object, UserAchievement):
        return render(request, 'share.html', {'name': name, 'description': description, 'share_urls': share_urls, 'type': 'achievement'})
    elif isinstance(user_object, UserChallenge):
        return render(request, 'share.html', {'name': name, 'description': description, 'share_urls': share_urls, 'type': 'challenge'})

def handle_share(request):
    type = unquote(request.GET.get('type'))
    name = unquote(request.GET.get('name'))
    site = unquote(request.GET.get('site'))
    share_url = unquote(request.GET.get('share_url'))
    try:
        user_achievement = UserAchievement.objects.create(user=request.user, achievement=Achievement.objects.get(name="First share"))
        user_activity = Activity.objects.create(user=request.user, image = "badges/first_share.png", name = "You've earned \"First share\" achievement", points = 15)
        activity_points(request, user_activity.points)
    except IntegrityError:
        pass
    user_activity = Activity.objects.create(user=request.user, image = "images/share.png", name = f'You\'ve shared \"{name}\" {type} post on {site}', points = 15)
    activity_points(request, user_activity.points)
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