
from .forms import SignUpForm, LogInForm, EditUserForm, CreateUserForm
from django.contrib.auth.forms import UserChangeForm
from .models import User
from .forms import SignUpForm, LogInForm, ExpenditureForm, CategoryForm
from .models import User, Category, Expenditure
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse_lazy
from django.views import generic
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
                if user.is_superuser == True:
                    return redirect('superuser_dashboard')
                else:
                    return redirect('landing_page')
        messages.add_message(request, messages.ERROR, "The credentials provided were invalid")
    form = LogInForm()
    return render(request, 'home.html', {'form': form})


def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            global_categories = Category.objects.filter(is_global = True)
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
        form=ExpenditureForm(request.POST, request.FILES)
        if form.is_valid():
            expenditure = form.save(commit=False)
            expenditure.user = request.user
            expenditure.save()
            return redirect('landing_page')
    else:
        form = ExpenditureForm()
    spendingList = Expenditure.objects.filter(user=request.user).order_by('-date_created')[0:19]
    return render(request, 'landing_page.html', {'form': form, 'spendings':spendingList, 'is_superuser': request.user.is_superuser})


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
    return render(request, 'expenditure_list.html', {'spendings':spendingList})

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
    paginator = Paginator(user_list, 3)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, 'superuser_dashboard.html', {'form': form, 'page': page})

def admin_dashboard(request):

    #DEFAULT PARAMETERS
    table_view = 'Users'
    table = 'user_table.html'
    user_list = User.objects.all()
    user_paginator = Paginator(user_list, 5)
    user_page_number = request.GET.get('page')
    page = user_paginator.get_page(user_page_number)
    user_form = CreateUserForm()
    category_form = CategoryForm()

    if request.method == 'POST':
        # IF CREATE USER BUTTON PRESSED
        if 'create_user' in request.POST:
            user_create_helper(request) #HELPER FUNCTION TO CLEAN UP

        if 'create_category' in request.POST:
            form = CategoryForm(request.POST)
            if form.is_valid():
                category = form.save()
                category.is_global = True
                category.save()
                return redirect('admin_dashboard')


        # IF UPDATE TABLE BUTTON PRESSED
        if 'table_update' in request.POST:
            table_view = request.POST['view_select']
            if table_view == "Users": #IF USERS SELECTED
                table = 'user_table.html'
                user_list = User.objects.all()
                user_paginator = Paginator(user_list, 5)
                user_page_number = request.GET.get('page')
                page = user_paginator.get_page(user_page_number)

            elif table_view == "Categories": #IF CATEGORIES SELECTED
                table = 'category_table.html'
                category_list = Category.objects.all()
                category_paginator = Paginator(category_list, 5)
                category_page_number = request.GET.get('page')
                page = category_paginator.get_page(category_page_number)

            else: #DEFAULT TO USERS
                table_view = 'Users'
                table = 'user_table.html'
                user_list = User.objects.all()
                user_paginator = Paginator(user_list, 5)
                user_page_number = request.GET.get('page')
                page = user_paginator.get_page(user_page_number)




    else: #DEFAULT TO USERS
        pass

    return render(request, 'admin_dashboard.html', {'page': page,'table': table,
    'table_header': table_view, 'user_form': user_form, 'category_form': category_form})

def user_create_helper(request):
    form = CreateUserForm(request.POST)
    if form.is_valid():
        user = form.save()
        return redirect('admin_dashboard')


def user_delete(request):
    if request.method == "POST":
        try:
            user_pk = request.POST['user_pk']
            u = User.objects.get(pk = user_pk)
            u.delete()
            return redirect('superuser_dashboard')

        except User.DoesNotExist:
            return redirect('superuser_dashboard')

def user_promote(request):
    if request.method == "POST":
        try:
            user_pk = request.POST['user_pk']
            u = User.objects.get(pk = user_pk)
            if u.is_staff == True:
                messages.info(request, 'This is a test')
            else:
                u.is_staff = True
                u.save()
            return redirect('superuser_dashboard')

        except User.DoesNotExist:
            return redirect('superuser_dashboard')

def user_demote(request):
    if request.method == "POST":
        try:
            user_pk = request.POST['user_pk']
            u = User.objects.get(pk = user_pk)
            if u.is_staff == False:
                messages.info(request, 'This is a test')
            else:
                u.is_staff = False
                u.save()
            return redirect('superuser_dashboard')

        except User.DoesNotExist:
            return redirect('superuser_dashboard')


# def display_expenditures(request):
#     expenditures = Expenditure.objects.all()
#     return render(request, 'expenditure_list.html', {'expenditures':expenditures})
