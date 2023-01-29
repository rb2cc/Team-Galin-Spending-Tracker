from .forms import SignUpForm, LogInForm
from .models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import user_passes_test

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
            login(request, user)
            return redirect('landing_page')
    else:
        form = SignUpForm()
    return render(request, 'sign_up.html', {'form': form})

def log_out(request):
    logout(request)
    return redirect('home')

def user_test(user):
    return user.is_anonymous==False

@user_passes_test(user_test, login_url='log_out')
def landing_page(request):
    return render(request, 'landing_page.html')