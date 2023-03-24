from django.shortcuts import redirect

# decorator that prevents logged in users from accessing views only intended
# to be viewed when logged out and redirects them to landing page or admin dashboard
def login_prohibited(view_function):
    def modified_view_function(request):
        if request.user.is_authenticated:
            if request.user.is_staff:
                return redirect('admin_dashboard')
            else:
                return redirect('landing_page')
        else:
            return view_function(request)
    return modified_view_function

# decorator that prevents logged out or anonymous in users from accessing views only intended
# to be viewed when logged in by redirecting them back to login page
def anonymous_prohibited(view_function):
    def modified_view_function(request):
        if request.user.is_authenticated==False:
            return redirect('home')
        else:
            return view_function(request)
    return modified_view_function

# decorator that prevents logged out or anonymous in users from accessing views only intended
# to be viewed when logged in by redirecting them back to login page
# this accommodates urls that also return an id or pk
def anonymous_prohibited_with_id(view_function):
    def modified_view_function(request, id):
        if request.user.is_authenticated==False:
            return redirect('home')
        else:
            return view_function(request, id)
    return modified_view_function

# decorator that prevents non-admin users from accessing a view by redirecting them back to the landing page
def user_prohibited(view_function):
    def modified_view_function(request):
        if request.user.is_staff==False or request.user.is_superuser==False: 
            return redirect('landing_page')
        else:
            return view_function(request)
    return modified_view_function

# decorator that prevents staff users from accessing a view by redirecting them back to admin dashboard
def admin_prohibited(view_function):
    def modified_view_function(request):
        if request.user.is_staff:
            return redirect('admin_dashboard')
        else:
            return view_function(request)
    return modified_view_function

# decorator that prevents super users that do not have super user permissions from accessing a view by redirecting them back to admin_home
def non_super_user_prohibited(view_function):
    def modified_view_function(request):
        if request.user.is_superuser==False:
            return redirect('admin_dashboard')
        else:
            return view_function(request)
    return modified_view_function
