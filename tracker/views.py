
from .forms import SignUpForm, LogInForm, EditUserForm
from django.contrib.auth.forms import UserChangeForm
from .models import User
from .forms import SignUpForm, LogInForm, ExpenditureForm
from .models import User, Category, Expenditure
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse_lazy
from django.views import generic
from datetime import date, timedelta, datetime
from django.utils import timezone

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
            user = form.save()
            global_categories = Category.objects.filter(is_global=True)
            user.available_categories.add(*global_categories)
            login(request, user)
            return redirect('landing_page')
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
        form = ExpenditureForm(request.POST, request.FILES)
        if form.is_valid():
            expenditure = form.save(commit=False)
            expenditure.user = request.user
            expenditure.save()
            return redirect('landing_page')
    else:
        form = ExpenditureForm()
    objectList = Expenditure.objects.filter(user=request.user)

    '''Data for list display'''
    spendingList = objectList.order_by('-date_created')[0:19]

    '''Data for chart display'''
    current_date = date.today()
    objectList7 = objectList.filter(date_created__range=(
        current_date-timezone.timedelta(days=6), current_date+timezone.timedelta(days=1)))
    objectList30 = objectList.filter(date_created__range=(
        current_date-timezone.timedelta(days=29), current_date+timezone.timedelta(days=1)))
    objectList90 = objectList.filter(date_created__range=(
        current_date-timezone.timedelta(days=89), current_date+timezone.timedelta(days=1)))
    dataTuple7 = getAllList(objectList7, 7)
    dataTuple30 = getAllList(objectList30, 30)
    dataTuple90 = getAllList(objectList90, 90)
    categoryList = {7: dataTuple7[0], 30: dataTuple30[0], 90: dataTuple90[0]}
    expenseList = {7: dataTuple7[1], 30: dataTuple30[1], 90: dataTuple90[1]}
    dateList = {7: dataTuple7[2], 30: dataTuple30[2], 90: dataTuple90[2]}
    dailyExpenseList = {7: dataTuple7[3], 30: dataTuple30[3], 90: dataTuple90[3]}
    cumulativeExpenseList = {7: dataTuple7[4], 30: dataTuple30[4], 90: dataTuple90[4]}

    return render(request, 'landing_page.html', {
        'form': form,
        'spendings': spendingList,
        'categoryList': categoryList,
        'expenseList': expenseList,
        'dateList': dateList,
        'dailyExpenseList': dailyExpenseList,
        'cumulativeExpenseList': cumulativeExpenseList,
    })


def getCategoryAndExpenseList(objectList):
    categoryList = []
    expenseList = []
    for x in Category.objects.all():
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


def getAllList(objectList, num):
    first = getCategoryAndExpenseList(objectList)
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


def expenditure_list(request):
    spendingList = Expenditure.objects.filter(user=request.user).order_by('-date_created')
    return render(request, 'expenditure_list.html', {'spendings': spendingList})


# def display_expenditures(request):
#     expenditures = Expenditure.objects.all()
#     return render(request, 'expenditure_list.html', {'expenditures':expenditures})


def forum_home(request):
    return render(request, 'forum/forum_home.html')


def posts(request):
    return render(request, 'forum/posts.html')


def detail(request):
    return render(request, 'forum/detail.html')
