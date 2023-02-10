from django.contrib.auth import views as auth_views


"""personal_spending_tracker URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from tracker import views
from tracker.views import UserEditView
from django.urls.conf import include  
from django.conf import settings  
from django.conf.urls.static import static  
from tracker.forms import UserPasswordResetForm



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('log_out/', views.log_out, name='log_out'),
    path('sign_up/', views.sign_up, name='sign_up'),
    path('landing_page/', views.landing_page, name='landing_page'),

    path('change_password', auth_views.PasswordChangeView.as_view(
        template_name='change_password.html', success_url='change_password_success'),  name='change_password'),
    path('change_password_success', views.change_password_success, name='change_password_success'),

    path('reset_password/', auth_views.PasswordResetView.as_view(
        template_name='password_reset_templates/password_reset.html', 
        form_class=UserPasswordResetForm), name="reset_password"),

    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(
        template_name='password_reset_templates/password_reset_sent.html'),
        name="password_reset_done"),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='password_reset_templates/password_reset_form.html'),
        name="password_reset_confirm"),

    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='password_reset_templates/password_reset_done.html'),
        name="password_reset_complete"),

    path('edit_user/', UserEditView.as_view(), name='edit_user'),
    path('expenditure_list', views.expenditure_list, name='expenditure_list')


]

if settings.DEBUG:  
        urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)  
