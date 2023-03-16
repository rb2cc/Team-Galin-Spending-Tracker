from .forms import AddCategoryForm, EditOverallForm
from .models import User, Category, Activity, UserAchievement
from django.shortcuts import redirect, render
from .views import activity_points

def category_list(request):
    user_id = request.user.id
    if request.method == 'POST':
        form=AddCategoryForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save(commit=False)
            category.save()
            request.user.available_categories.add(category)
            user_activity_name = f'You\'ve added \"{category.name}\" category with {category.week_limit} week limit'
            user_activity = Activity.objects.create(user=request.user, image = "images/category.png", name = user_activity_name, points = 15)
            activity_points(request, user_activity.points)
            overall = overall = Category.objects.filter(is_overall = True).get(users__id=request.user.id)
            overall.week_limit += category.week_limit
            overall.save(force_update = True)
            return redirect('category_list')
    else:
        form = AddCategoryForm()
    categoryList = Category.objects.filter(users__id=user_id).filter(is_overall=False).order_by('name')
    overall = Category.objects.filter(users__id=user_id).get(is_overall=True)
    if categoryList.count() == 1:
        try:
            try:
                user_achievement = UserAchievement.objects.create(user=request.user, achievement=Achievement.objects.get(name="Budget boss"))
            except ObjectDoesNotExist:
                pass
            user_activity = Activity.objects.create(user=request.user, image = "badges/budget_boss.png", name = "You've earned \"Budget boss\" achievement", points = 15)
            activity_points(request, user_activity.points)
        except IntegrityError:
            pass
    return render(request, 'category_list.html', {'categories':categoryList, 'form':form, 'overall':overall})

def remove_category(request, id):
    category = Category.objects.get(id = id)
    category_name = category.name
    diff = category.week_limit
    if category.is_global:
        request.user.available_categories.remove(category)
    else:
        category.delete()
    user_activity = Activity.objects.create(user=request.user, image = "images/delete.png", name = f'You\'ve deleted \"{category_name}\" category')
    overall = Category.objects.filter(is_overall = True).get(users__id=request.user.id)
    overall.week_limit -= diff
    overall.save(force_update = True)
    return redirect('category_list')

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
                    user_activity = Activity.objects.create(user=request.user, image = "images/edit.png", name = activity_name)
                if (category.week_limit != category_week_limit):
                    activity_name = f'You\'ve changed \"{category.name}\" category week limit from {category_week_limit} to {category.week_limit}'
                    user_activity = Activity.objects.create(user=request.user, image = "images/edit.png", name = activity_name)
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
                    user_activity = Activity.objects.create(user=request.user, image = "images/edit.png", name = activity_name)
                return redirect('category_list')
    else:
        if category.is_overall==False:
            form = AddCategoryForm(instance=category)
        else:
            form = EditOverallForm(instance=category, user = current_user)
    return render(request, 'edit_category.html', {'form' : form})