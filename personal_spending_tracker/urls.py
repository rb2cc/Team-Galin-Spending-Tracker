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
    path('expenditure_list/', views.expenditure_list, name='expenditure_list'),
    path('forum_home/', views.forum_home, name='forum_home'),
    path('posts/', views.posts, name='posts'),
    path('detail/', views.detail, name='detail'),
    # path('update_expenditures/',views.update_expenditures, name='update_expenditures'),
    path('category_list', views.category_list, name='category_list'),
    path('remove_category/<int:id>', views.remove_category, name='remove_category'),
    path('remove_expenditure/', views.remove_expenditure, name='remove_expenditure'),
    path('update_expenditure', views.update_expenditure, name='update_expenditure'),
    path('search_expenditure/', views.search_expenditure, name='search_expenditure'),
    path('search_category/', views.search_category, name='search_category'),
    path('edit_category/<int:id>', views.edit_category, name='edit_category'),
    path('challenge_list/', views.challenge_list, name='challenge_list'),
    path('challenge_details/<int:id>/', views.challenge_details, name='challenge_details'),
    path('enter_challenge/', views.enter_challenge, name='enter_challenge'),
    path('my_challenges/', views.my_challenges, name='my_challenges'),
    path('share_challenge/<int:id>', views.share_challenge, name='share_challenge'),
    path('handle_share/', views.handle_share, name='handle_share'),
    path('achievement_list/', views.achievement_list, name='achievement_list'),
    path('my_achievements/', views.my_achievements, name='my_achievements'),
    path('share_achievement/<int:id>', views.share_achievement, name='share_achievement'),
    path('share/', views.share, name='share')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
