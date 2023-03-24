from .forms import ExpenditureForm
from .models import Category, Expenditure, Activity
from django.shortcuts import redirect, render
from django.utils.datastructures import MultiValueDictKeyError
from .helpers import anonymous_prohibited, anonymous_prohibited_with_id

#Gets all expenditures under the filters of belonging to the current user, is not binned and ordered by latest date
#Returns both expenditure data and category data which is filtered by what user the category belongs to
@anonymous_prohibited
def expenditure_list(request):
    spending_list = Expenditure.objects.filter(user=request.user, is_binned=False, category__is_binned=False).order_by('-date_created')
    categories = Category.objects.filter(users__id=request.user.id, is_binned=False, is_overall=False)
    return render(request, 'expenditure_list.html', {'spendings': spending_list, 'categories': categories})

#Gets all expenditures under the filter of being binned
@anonymous_prohibited
def binned_expenditure_list(request):
    binned_list = Expenditure.objects.filter(user=request.user, is_binned=True).order_by('-date_created')
    categories = Category.objects.filter(users__id=request.user.id)
    return render(request, 'expenditure_bin.html', {'binned_spendings': binned_list, 'categories': categories})

#checks if the total number of expenditure objects inside the bin is greater than 10
#if greater than 10 the bin gets emptied (all objects are deleted) otherwise pass
def overflow_delete_expenditures(request):
    expenditures = Expenditure.objects.filter(user=request.user, is_binned=True)
    if expenditures.count() > 10:
        expenditures.delete()
    else:
        pass

#Gets id field of the selected expenditure radio button and changes the is_binned field from false to true
#This effectively moves the expenditure from the expenditure list page to the expenditure bin page
@anonymous_prohibited
def bin_expenditure(request):
    if request.method == "POST":
        try:
            expenditure_pk = request.POST['radio_pk']
            expenditure = Expenditure.objects.get(pk=expenditure_pk)
            expenditure.is_binned = True
            expenditure.save()
            overflow_delete_expenditures(request)
            Activity.objects.create(user=request.user, image = "images/delete.png", name = f'You\'ve put \"{expenditure.title}\" expenditure in the bin')
            return redirect('expenditure_list')
        except Expenditure.DoesNotExist:
            return redirect('expenditure_list')
        except MultiValueDictKeyError:
            return redirect('expenditure_list')

#Gets id field of the selected expenditure recover button and changes the is_binned field from true to false
#This effectively moves the expenditure from the expenditure bin page to the expenditure list page
@anonymous_prohibited
def recover_expenditure(request):
    if request.method == "POST":
        try:
            expenditure_pk = request.POST['radio_pk']
            expenditure = Expenditure.objects.get(pk=expenditure_pk)
            expenditure.is_binned = False
            expenditure.save()
            Activity.objects.create(user=request.user, image = "images/recover.png", name = f'You\'ve recovered \"{expenditure.title}\" expenditure from the bin')
            return redirect('expenditure_bin')
        except Expenditure.DoesNotExist:
            return redirect('expenditure_bin')
        except MultiValueDictKeyError:
            return redirect('expenditure_bin')
        
#Gets id field of the selected expenditure delete button and deletes the expenditure object from the database
@anonymous_prohibited
def delete_expenditure(request):
    if request.method == "POST":
        try:
            expenditure_pk = request.POST['radio_pk']
            expenditure = Expenditure.objects.get(pk=expenditure_pk)
            expenditure_title = expenditure.title
            expenditure.delete()
            Activity.objects.create(user=request.user, image = "images/delete.png", name = f'You\'ve deleted \"{expenditure_title}\" expenditure')
            return redirect('expenditure_bin')
        except Expenditure.DoesNotExist:
            return redirect('expenditure_bin')
        except MultiValueDictKeyError:
            return redirect('expenditure_bin')

#Gets selected expenditure object and returns its form allowing the user to change its fields and saves the changes
@anonymous_prohibited_with_id
def update_expenditure(request, id):
    expenditure = Expenditure.objects.get(id = id)
    previous_title = expenditure.title
    previous_expense = int(expenditure.expense)
    previous_description = expenditure.description
    previous_category = expenditure.category.name
    form  = ExpenditureForm(instance = expenditure, r=request)
    if request.POST:
        form = ExpenditureForm(request.POST, request.FILES, instance = expenditure, r=request)
        if form.is_valid():
            expenditure = form.save(commit=False)
            expenditure.save() #save the updated form inputs
            create_expenditure_activity(request, expenditure, previous_title, previous_expense, previous_description, previous_category)
            return redirect('expenditure_list')
    categories = Category.objects.filter(users__id=request.user.id)
    return render(request, 'update_expenditure.html', {'form' : form, 'categories':categories} )

#Reloads page to display expenditures that contain the text input from the search bar in their title field
@anonymous_prohibited
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
@anonymous_prohibited
def filter_by_category(request):
    query = request.GET.get("q")
    categories = Category.objects.filter(users__id=request.user.id)

    if (query == None or query == "All"):
        expenditures = Expenditure.objects.filter(user=request.user, is_binned=False).order_by('-date_created')
        return render(request, 'expenditure_list.html', {'spendings': expenditures, 'categories': categories})
    else:
        expenditures = Expenditure.objects.all().filter(user=request.user, category=query, is_binned=False).order_by('-date_created')
        return render(request, 'expenditure_list.html', {'spendings': expenditures, 'categories': categories})

#Reloads page to display expenditures after filtering them with a miscellaneous characteristic e.g. latest, oldest, most expensive, least expensive
@anonymous_prohibited
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

#Creates activity objects when expenditure actions occur such that they will appear on the activty
def create_expenditure_activity(request, expenditure, previous_title, previous_expense, previous_description, previous_category):
    if (expenditure.title != previous_title):
        activity_name = f'You\'ve changed \"{previous_title}\" expenditure title to \"{expenditure.title}\"'
        Activity.objects.create(user=request.user, image = "images/edit.png", name = activity_name)
    if (expenditure.expense != previous_expense):
        activity_name = f'You\'ve changed \"{expenditure.title}\" expenditure expense from {previous_expense} to {expenditure.expense}'
        Activity.objects.create(user=request.user, image = "images/edit.png", name = activity_name)
    if (expenditure.description != previous_description):
        activity_name = f'You\'ve changed \"{expenditure.title}\" expenditure description from \"{previous_description}\" to \"{expenditure.description}\"'
        Activity.objects.create(user=request.user, image = "images/edit.png", name = activity_name)
    if (expenditure.category.name != previous_category):
        activity_name = f'You\'ve changed \"{expenditure.title}\" expenditure category from \"{previous_category}\" to \"{expenditure.category.name}\"'
        Activity.objects.create(user=request.user, image = "images/edit.png", name = activity_name)

