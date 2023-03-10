
from .forms import SignUpForm, LogInForm, EditUserForm, ReportForm
from django.contrib.auth.forms import UserChangeForm
from .models import User
from .forms import SignUpForm, LogInForm, ExpenditureForm, AddCategoryForm, EditOverallForm
from .models import User, Category, Expenditure, Challenge, UserChallenge, Achievement, UserAchievement, Level, UserLevel, Post, Forum_Category
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

from .utils import update_views

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
                user_achievement = UserAchievement.objects.create(user=request.user, achievement = Achievement.objects.get(name="New user"))
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
    categoryList = Category.objects.filter(users__id=user_id).filter(is_overall=False).order_by('name')
    overall = Category.objects.filter(users__id=user_id).get(is_overall=True)
    if categoryList.count() == 1:
        try:
            user_achievement = UserAchievement.objects.create(user=request.user, achievement=Achievement.objects.get(name="Budget boss"))
        except IntegrityError:
            pass
    return render(request, 'category_list.html', {'categories':categoryList, 'form':form, 'overall':overall})

def remove_category(request, id):
    category = Category.objects.get(id = id)
    diff = category.week_limit
    if category.is_global:
        request.user.available_categories.remove(category)
    else:
        category.delete()
    overall = Category.objects.filter(is_overall = True).get(users__id=request.user.id)
    overall.week_limit -= diff
    overall.save(force_update = True)
    return redirect('category_list')

def edit_category(request, id):
    current_user = request.user
    category = Category.objects.get(id = id)
    before_limit = category.week_limit
    if request.method == "POST":
        if category.is_overall==False:
            form = AddCategoryForm(request.POST, instance = category)
            if form.is_valid():
                category = form.save(commit=False)
                category.save()
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
                return redirect('category_list')
    else:
        if category.is_overall==False:
            form = AddCategoryForm(instance=category)
        else:
            form = EditOverallForm(instance=category, user = current_user)
    return render(request, 'edit_category.html', {'form' : form})
    
def forum_home(request):
    all_forum_categories = Forum_Category.objects.all()
    context = {
        "all_forum_categories": all_forum_categories,
    }
    return render(request, 'forum/forum_home.html', context)

def posts(request, slug):
    category = get_object_or_404(Forum_Category, slug=slug)
    posts = Post.objects.filter(approved=True, forum_categories=category)

    context = {
        "posts":posts,
        "forum": category,

    }
  
    return render(request, 'forum/posts.html', context)

def detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    context = {
        "post":post
    }
    update_views(request, post)
    return render(request, 'forum/detail.html', context)

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
        previous_average_difference = average_daily-previous_average
    else:
        previous_average_difference = previous_average-average_daily
        
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



