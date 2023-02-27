from .forms import ExpenditureForm
from .models import Category, Expenditure
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.utils.datastructures import MultiValueDictKeyError

def expenditure_list(request):
    spending_list = Expenditure.objects.filter(user=request.user, is_binned=False).order_by('-date_created')
    categories = Category.objects.filter(users__id=request.user.id)
    return render(request, 'expenditure_list.html', {'spendings': spending_list, 'categories': categories})

def binned_expenditure_list(request):
    binned_list = Expenditure.objects.filter(user=request.user, is_binned=True).order_by('-date_created')
    categories = Category.objects.filter(users__id=request.user.id)
    return render(request, 'expenditure_bin.html', {'binned_spendings': binned_list, 'categories': categories})

def bin_expenditure(request):
    if request.method == "POST":
        try:
            expenditure_pk = request.POST['radio_pk']
            expenditure = Expenditure.objects.get(pk=expenditure_pk)
            expenditure.is_binned = True
            expenditure.save()
            return redirect('expenditure_list')
        except Expenditure.DoesNotExist:
            return redirect('expenditure_list')
        except MultiValueDictKeyError:
            return redirect('expenditure_list')
        
def recover_expenditure(request):
    if request.method == "POST":
        try:
            expenditure_pk = request.POST['radio_pk']
            expenditure = Expenditure.objects.get(pk=expenditure_pk)
            expenditure.is_binned = False
            expenditure.save()
            return redirect('expenditure_bin')
        except Expenditure.DoesNotExist:
            return redirect('expenditure_bin')
        except MultiValueDictKeyError:
            return redirect('expenditure_bin')
        
def delete_expenditure(request):
    if request.method == "POST":
        try:
            expenditure_pk = request.POST['radio_pk']
            expenditure = Expenditure.objects.get(pk=expenditure_pk)
            expenditure.delete()
            return redirect('expenditure_bin')
        except Expenditure.DoesNotExist:
            return redirect('expenditure_bin')
        except MultiValueDictKeyError:
            return redirect('expenditure_bin')

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
        expenditures = Expenditure.objects.filter(user=request.user, is_binned=False).order_by('-date_created')
        return render(request, 'expenditure_list.html', {'spendings': expenditures, 'categories': categories})
    else:
        expenditures = Expenditure.objects.all().filter(user=request.user, title__icontains=query, is_binned=False).order_by('-date_created')
        return render(request, 'expenditure_list.html', {'spendings': expenditures, 'categories': categories})

def filter_by_category(request):
    query = request.GET.get("q")
    categories = Category.objects.filter(users__id=request.user.id)

    if (query == None or query == "All"):
        expenditures = Expenditure.objects.filter(user=request.user, is_binned=False).order_by('-date_created')
        return render(request, 'expenditure_list.html', {'spendings': expenditures, 'categories': categories})
    else:
        expenditures = Expenditure.objects.all().filter(user=request.user, category=query, is_binned=False).order_by('-date_created')
        return render(request, 'expenditure_list.html', {'spendings': expenditures, 'categories': categories})

def filter_by_miscellaneous(request):
    query = request.GET.get("q")
    categories = Category.objects.filter(users__id=request.user.id)

    if (query == "desc"):
        expenditures = Expenditure.objects.filter(is_binned=False).order_by('-expense')
        return render(request, 'expenditure_list.html', {'spendings': expenditures, 'categories': categories})
    elif (query == "asc"):
        expenditures = Expenditure.objects.filter(is_binned=False).order_by('expense')
        return render(request, 'expenditure_list.html', {'spendings': expenditures, 'categories': categories})
    elif (query == "old"):
        expenditures = Expenditure.objects.filter(is_binned=False).order_by('date_created')
        return render(request, 'expenditure_list.html', {'spendings': expenditures, 'categories': categories})
    elif (query == "new"):
        expenditures = Expenditure.objects.filter(is_binned=False).order_by('-date_created')
        return render(request, 'expenditure_list.html', {'spendings': expenditures, 'categories': categories})

