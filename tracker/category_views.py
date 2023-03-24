from .forms import AddCategoryForm, EditOverallForm
from .models import Category, Activity, UserAchievement, Expenditure, Achievement
from django.shortcuts import redirect, render
from .views import activity_points
from dateutil.relativedelta import relativedelta, MO, SU
from django.utils import timezone
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from .helpers import anonymous_prohibited, anonymous_prohibited_with_id
from django.utils.datastructures import MultiValueDictKeyError

#Collects all categories belonging to the request user and returns the data to the
# category list view and redirects to that page
@anonymous_prohibited
def category_list(request):
    user_id = request.user.id
    if request.method == 'POST':
        form=AddCategoryForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save(commit=False)
            category.save()
            request.user.available_categories.add(category)
            try:
                try:
                    UserAchievement.objects.create(user=request.user, achievement=Achievement.objects.get(name="Budget boss"))
                except ObjectDoesNotExist:
                    pass
                user_activity = Activity.objects.create(user=request.user, image = "badges/budget_boss.png", name = "You've earned \"Budget boss\" achievement", points = 15)
                activity_points(request, user_activity.points)
            except IntegrityError:
                pass
            user_activity_name = f'You\'ve added \"{category.name}\" category with {category.week_limit} week limit'
            user_activity = Activity.objects.create(user=request.user, image = "images/category.png", name = user_activity_name, points = 15)
            activity_points(request, user_activity.points)
            overall = Category.objects.filter(is_overall = True).get(users__id=request.user.id)
            overall.week_limit += category.week_limit
            overall.save(force_update = True)
            return redirect('category_list')
    else:
        form = AddCategoryForm()
    categoryList = Category.objects.filter(users__id=user_id).filter(is_overall=False, is_binned=False).order_by('name')
    overall = Category.objects.filter(users__id=user_id).get(is_overall=True)
    return render(request, 'category_list.html', {'categories':categoryList, 'form':form, 'overall':overall})

# gets the correct category object using the id argument and returns its form
# validates the data again before saving
# also generates activity objects for the activity page to keep record of when a category is edited
@anonymous_prohibited_with_id
def edit_category(request, id):
    current_user = request.user
    category = Category.objects.get(id = id)
    category_name = category.name
    category_week_limit = category.week_limit
    before_limit = category.week_limit
    if request.method == "POST":
        if category.is_overall==False:
            form = AddCategoryForm(request.POST, instance = category)
            if form.is_valid():
                category = form.save(commit=False)
                category.save()
                if (category.name != category_name):
                    activity_name = f'You\'ve changed \"{category_name}\" category name to \"{category.name}\"'
                    Activity.objects.create(user=request.user, image = "images/edit.png", name = activity_name)
                if (category.week_limit != category_week_limit):
                    activity_name = f'You\'ve changed \"{category.name}\" category week limit from {category_week_limit} to {category.week_limit}'

                    Activity.objects.create(user=request.user, image = "images/edit.png", name = activity_name)
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
                if (category.week_limit != category_week_limit):
                    activity_name = f'You\'ve changed \"{category.name}\" category week limit from {category_week_limit} to {category.week_limit}'
                    Activity.objects.create(user=request.user, image = "images/edit.png", name = activity_name)
                return redirect('category_list')
    else:
        if category.is_overall==False:
            form = AddCategoryForm(instance=category)
        else:
            form = EditOverallForm(instance=category, user = current_user)
    return render(request, 'edit_category.html', {'form' : form})

# function used to calculate how close categories are to their weekly limit and
# assigns a colour to the bar dependent on the percentage calculated
# helps visualise spending to the user 
def category_progress(request, offset):

    def _make_percent(num, category, user):
        denom = category.week_limit
        percent = int(100 * (float(num) / float(denom)))
        if percent > 100:
            return 100
        return percent

    def _get_colour(percent):
        if percent == 100:
            return "#FF2B2B"
        elif percent >= 75:
            return "#F2B933"
        elif percent >= 50:
            return "#118DD5"
        else:
            return "#4CAF50"

    user = request.user
    week_start = timezone.now().date() + relativedelta(weekday=MO(-1-offset))
    week_end = week_start + relativedelta(weekday=SU(1)) 
    categories = Category.objects.filter(is_overall = False).filter(users__id = user.id)
    val_dict = {}
    for category in categories:
        val_dict[category.name] = 0
    expenditures = Expenditure.objects.filter(user=user, date_created__gte=week_start, date_created__lte=week_end,
                                              is_binned=False)
    for expenditure in expenditures:
        val_dict[expenditure.category.name] += expenditure.expense  # dict from category name -> total expense
    overall_spend = sum(val_dict.values())
    overall = Category.objects.filter(users__id=user.id).get(is_overall=True)
    overall_percent = _make_percent(overall_spend, overall, user)
    overall_colour = _get_colour(overall_percent)
    val_dict = {k: _make_percent(v, Category.objects.filter(users__id=user.id, name=k).first(), user) for k, v in
                val_dict.items()}
    val_dict = {k: (v, _get_colour(v)) for k, v in val_dict.items()}
    prev_week = offset + 1
    next_week = offset -1
    if next_week < 0:
        next_week = 0
    return render(request, 'category_progress.html', {
        'cat_map':val_dict,
        'overall_percent':overall_percent,
        'overall_colour':overall_colour,
        'offset':offset,
        'start':week_start,
        'end':week_end,
        'prev':prev_week,
        'next':next_week,
    })

#checks if the number of category objects inside the bin are greater than 0
#if greater than 10 then the bin gets emptied (all objects get deleted)
def overflow_delete_categories(request):
    categories = Category.objects.filter(users__id=request.user.id).filter(is_overall=False, is_binned=True)
    if categories.count() > 10:
        categories.delete()
    else:
        pass 

#gets correct category object using the id argument and changes their is_binned flag from False to True
#in turn any expenditures with the category also has in_binned changed to True
@anonymous_prohibited_with_id
def bin_category(request, id):
    category = Category.objects.get(id = id)
    diff = category.week_limit
    if category.is_global:
        request.user.available_categories.remove(category)
    else:
        category.is_binned = True
        category.save()
    expenditures_of_category=Expenditure.objects.filter(is_binned=False,category=category)
    for expenditure in expenditures_of_category:
        expenditure.is_binned = True
        expenditure.save()
    overflow_delete_categories(request)
    Activity.objects.create(user=request.user, image = "images/delete.png", name = f'You\'ve put \"{category.name}\" category with all its expenditures in the bin')
    overall = Category.objects.filter(is_overall = True).get(users__id=request.user.id)
    overall.week_limit -= diff
    overall.save(force_update = True)
    return redirect('category_list')

#gets correct category object using the id argument and deletes them from the database
#in turn any expenditures with the category also are deleted
@anonymous_prohibited
def delete_category(request):
    if request.method == "POST":
        try:
            category_pk = request.POST['radio_pk']
            category = Category.objects.get(pk=category_pk)
            category_name = category.name
            category.delete()
            Activity.objects.create(user=request.user, image = "images/delete.png", name = f'You\'ve deleted \"{category_name}\" category with all its expenditures')
            return redirect('category_bin')
        except MultiValueDictKeyError:
            return redirect('category_bin')
    else:
        return redirect('category_bin')

#Gets id field of the selected expenditure recover button and changes the is_binned field from true to false
# effectively moves the category from category bin to category list
@anonymous_prohibited
def recover_category(request):
    if request.method == "POST":
        try:
            category_pk = request.POST['radio_pk']
            category = Category.objects.get(pk=category_pk)
            category.is_binned = False
            category.save()
            overall = Category.objects.filter(is_overall = True).get(users__id=request.user.id)
            overall.week_limit += category.week_limit
            overall.save(force_update = True)
            expenditures_of_category=Expenditure.objects.filter(is_binned=True, category=category)
            for expenditure in expenditures_of_category:
                expenditure.is_binned = False
                expenditure.save()
            Activity.objects.create(user=request.user, image = "images/recover.png", name = f'You\'ve recovered \"{category.name}\" category with all its expenditures from the bin')
            return redirect('category_bin')
        except MultiValueDictKeyError:
            return redirect('category_bin')
    else:
        return redirect('category_bin')

#Gets all expenditures under the filter of being binned and passes the data into the binned category list
@anonymous_prohibited
def binned_category_list(request):
    binned_list = Category.objects.filter(users__id=request.user.id).filter(is_overall=False, is_binned=True).order_by('name')
    return render(request, 'category_bin.html', {'binned_categories': binned_list})
