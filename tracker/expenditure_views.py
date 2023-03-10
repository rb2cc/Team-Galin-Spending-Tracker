from .forms import ExpenditureForm
from .models import Category, Expenditure
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.utils.datastructures import MultiValueDictKeyError

#Gets all expenditures under the filters of belonging to the current user, is not binned and ordered by latest date
#Returns both expenditure data and category data which is filtered by what user the category belongs to
def expenditure_list(request):
    spending_list = Expenditure.objects.filter(user=request.user, is_binned=False).order_by('-date_created')
    categories = Category.objects.filter(users__id=request.user.id)
    return render(request, 'expenditure_list.html', {'spendings': spending_list, 'categories': categories})

#Gets all expenditures under the filter of being binned
def binned_expenditure_list(request):
    binned_list = Expenditure.objects.filter(user=request.user, is_binned=True).order_by('-date_created')
    categories = Category.objects.filter(users__id=request.user.id)
    return render(request, 'expenditure_bin.html', {'binned_spendings': binned_list, 'categories': categories})

#Gets id field of the selected expenditure radio button and changes the is_binned field from false to true
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

#Gets id field of the selected expenditure recover button and changes the is_binned field from true to false
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
        
#Gets id field of the selected expenditure delete button and deletes the object from the database
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

#Gets selected expenditure object and returns its form allowing changing of its fields and saves the changes
def update_expenditure(request, id):
    expenditure = Expenditure.objects.get(id = id) 
    form  = ExpenditureForm(instance = expenditure, r=request)
    if request.POST:
        form = ExpenditureForm(request.POST, request.FILES, instance = expenditure, r=request)
        if form.is_valid():
            expenditure = form.save(commit=False)
            expenditure.save() #save the updated form inputs
            return redirect('expenditure_list')
    categories = Category.objects.filter(users__id=request.user.id)
    return render(request, 'update_expenditure.html', {'form' : form, 'categories':categories} )

#Reloads page to display expenditures that contain the text input from the search bar in their title field
def filter_by_title(request):
    query = request.GET.get("q")
    categories = Category.objects.filter(users__id=request.user.id)
    if (query == None):
        expenditures = Expenditure.objects.filter(user=request.user, is_binned=False).order_by('-date_created')
        return render(request, 'expenditure_list.html', {'spendings': expenditures, 'categories': categories})
    else:
        expenditures = Expenditure.objects.all().filter(user=request.user, title__icontains=query, is_binned=False).order_by('-date_created')
        return render(request, 'expenditure_list.html', {'spendings': expenditures, 'categories': categories})

#Reloads page to display expenditures that are of the category the user selected from the dropdown box
def filter_by_category(request):
    query = request.GET.get("q")
    categories = Category.objects.filter(users__id=request.user.id)

    if (query == None or query == "All"):
        expenditures = Expenditure.objects.filter(user=request.user, is_binned=False).order_by('-date_created')
        return render(request, 'expenditure_list.html', {'spendings': expenditures, 'categories': categories})
    else:
        expenditures = Expenditure.objects.all().filter(user=request.user, category=query, is_binned=False).order_by('-date_created')
        return render(request, 'expenditure_list.html', {'spendings': expenditures, 'categories': categories})

#Reloads page to display expenditures after filtering them with a miscellaneous characteristic
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

