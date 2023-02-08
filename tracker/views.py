
from .forms import SignUpForm, LogInForm, EditUserForm
from django.contrib.auth.forms import UserChangeForm
from .models import User
from .forms import SignUpForm, LogInForm, ExpenditureForm, AddCategoryForm
from .models import User, Category, Expenditure
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse_lazy
from django.views import generic

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
    return render(request, 'landing_page.html', {'form': form, 'spendings':spendingList})


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
    categoryList = Category.objects.filter(users__id=user_id).order_by('is_global')
    return render(request, 'category_list.html', {'categories':categoryList, 'form':form})

def remove_category(request, id):
    category = Category.objects.get(id = id)
    if category.is_global:
        request.user.available_categories.remove(category)
    else:
        category.delete()
    return redirect('category_list')

    
# def display_expenditures(request):
#     expenditures = Expenditure.objects.all()
#     return render(request, 'expenditure_list.html', {'expenditures':expenditures})

