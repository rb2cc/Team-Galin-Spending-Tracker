from django.shortcuts import redirect

# decorator that prevents logged in users from accessing views by redirecting them back to 
def login_prohibited(view_function):
    def modified_view_function(request):
        if request.user.is_authenticated:
            if request.user.is_staff:
                return redirect('admin_home')
            else:
                return redirect('landing_page')
        else:
            return view_function(request)
    return modified_view_function

# decorator that prevents student users from accessing a view by redirecting them back to student_home
def student_prohibited(view_function):
    def modified_view_function(request):
        if request.user.is_staff==False: 
            return redirect('landing_page')
        else:
            return view_function(request)
    return modified_view_function

# decorator that prevents admin users from accessing a view by redirecting them back to admin_home
def admin_prohibited(view_function):
    def modified_view_function(request):
        if request.user.is_staff:
            return redirect('admin_home')
        else:
            return view_function(request)
    return modified_view_function

# decorator that prevents admins that do not have super user permissions from accessing a view by redirecting them back to admin_home
def non_super_user_prohibited(view_function):
    def modified_view_function(request):
        if request.user.is_superuser==False:
            return redirect('admin_home')
        else:
            return view_function(request)
    return modified_view_function
