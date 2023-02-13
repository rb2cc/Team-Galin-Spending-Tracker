from .forms import SignUpForm, LogInForm, ExpenditureForm
from .models import User, Category, Challenge, UserChallenge, Achievement
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import user_passes_test, login_required
from django.db import IntegrityError

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
    return user.is_anonymous==False

@user_passes_test(user_test, login_url='log_out')
def landing_page(request):
    return render(request, 'landing_page.html')

def expenditure_list(request):
    return render(request, 'expenditure_list.html')

def create_expenditure(request):
    if request.method == 'POST':
        form=ExpenditureForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('expenditure_list')
        messages.add_message(request, messages.ERROR, "The inputs provided were invalid")

    else:
        form = ExpenditureForm()
    return render(request, 'create_expenditure.html', {'form': form})

def challenge_list(request):
    challenges = Challenge.objects.all()
    context = {
        'challenges': challenges,
    }
    return render(request, 'challenge_list.html', context)

def achievement_list(request):
    user = request.user
    achievements = Achievement.objects.filter(user=user)
    context = {
        'achievements': achievements,
    }
    return render(request, 'achievement_list.html', context)

def challenge_details(request, id):
    challenge = Challenge.objects.get(id=id)
    return render(request, 'challenge_details.html', {'challenge': challenge})

def enter_challenge(request):
    try:
        if request.method == 'POST':
            challenge_id = request.POST['challenge_id']
            user_challenge = UserChallenge(user=request.user, challenge_id=challenge_id)
            user_challenge.save()
            return redirect('my_challenges')
    except IntegrityError:
        messages.error(request, 'You have already entered this challenge.')
        return redirect('challenge_list')

@login_required
def my_challenges(request):
    user_challenges = UserChallenge.objects.filter(user=request.user)
    return render(request, 'my_challenges.html', {'user_challenges': user_challenges})