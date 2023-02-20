from .forms import SignUpForm, LogInForm, EditUserForm
from django.contrib.auth.forms import UserChangeForm
from .models import User
from .forms import SignUpForm, LogInForm, ExpenditureForm, AddCategoryForm
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

def expenditure_list(request):
    spendingList = Expenditure.objects.filter(user=request.user).order_by('-date_created')
    categories = Category.objects.filter(users__id=request.user.id)
    return render(request, 'expenditure_list.html', {'spendings': spendingList, 'categories': categories})

def remove_expenditure(request):
    if request.method == "POST":
        try:
            expenditure_pk = request.POST['radio_pk']
            expenditure = Expenditure.objects.get(pk=expenditure_pk)
            expenditure.delete()
            return redirect('expenditure_list')
        except Expenditure.DoesNotExist:
            return redirect('expenditure_list')
        except MultiValueDictKeyError:
            return redirect('expenditure_list')

def update_expenditure(request, id):
    expenditure = Expenditure.objects.get(id = id) 
    form  = ExpenditureForm(instance = expenditure, r=request)
    if request.POST:
        form = ExpenditureForm(request.POST, instance = expenditure, r=request)
        if form.is_valid():
            expenditure = form.save(commit=False)
            expenditure.save() #save the updated form inputs
            return redirect('expenditure_list')
    categories = Category.objects.filter(users__id=request.user.id)
    return render(request, 'update_expenditure.html', {'form' : form, 'categories':categories} )

def filter_by_title(request):
    query = request.GET.get("q")
    categories = Category.objects.filter(users__id=request.user.id)
    if (query == None):
        expenditures = Expenditure.objects.filter(user=request.user).order_by('-date_created')
        return render(request, 'expenditure_list.html', {'spendings': expenditures, 'categories': categories})
    else:
        expenditures = Expenditure.objects.all().filter(user=request.user, title__icontains=query).order_by('-date_created')
        return render(request, 'expenditure_list.html', {'spendings': expenditures, 'categories': categories})

def filter_by_category(request):
    query = request.GET.get("q")
    categories = Category.objects.filter(users__id=request.user.id)

    if (query == None or query == "All"):
        expenditures = Expenditure.objects.filter(user=request.user).order_by('-date_created')
        return render(request, 'expenditure_list.html', {'spendings': expenditures, 'categories': categories})
    else:
        expenditures = Expenditure.objects.all().filter(user=request.user, category=query).order_by('-date_created')
        return render(request, 'expenditure_list.html', {'spendings': expenditures, 'categories': categories})