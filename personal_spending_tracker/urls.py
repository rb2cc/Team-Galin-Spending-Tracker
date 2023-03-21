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
from django.urls import re_path, path
from tracker import views, expenditure_views, category_views
from tracker.views import UserEditView
from django.urls.conf import include
from django.conf import settings
from django.conf.urls.static import static
from tracker.forms import UserPasswordResetForm


urlpatterns = [
    #paths concerning admin and basic sign-up/landing pages
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('log_out/', views.log_out, name='log_out'),
    path('sign_up/', views.sign_up, name='sign_up'),
    path('landing_page/', views.landing_page, name='landing_page'),
    path('notifications/', views.notifications, name='notifications'),

    #paths concerning password reset
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

    #paths concerning garden, report and user editing
    path('garden/', views.garden, name='garden'),
    path('save-item-position/', views.save_item_position, name='save_item_position'),
    path('report/', views.report, name='report'),
    path('edit_user/', UserEditView.as_view(), name='edit_user'),

    #paths concerning categories
    path('bin_category/<int:id>', category_views.bin_category, name='bin_category'),
    path('recover_category', category_views.recover_category, name='recover_category'),
    path('delete_category', category_views.delete_category, name="delete_category"),
    path('category_list', category_views.category_list, name='category_list'),
    path('remove_category/<int:id>', category_views.remove_category, name='remove_category'),
    path('edit_category/<int:id>', category_views.edit_category, name='edit_category'),
    path('category_progress/<int:offset>', category_views.category_progress, name='category_progress'),
    path('category_bin/', category_views.binned_category_list, name='category_bin'),

    #paths concerning expenditures
    path('expenditure_list/', expenditure_views.expenditure_list, name='expenditure_list'),
    path('bin_expenditure', expenditure_views.bin_expenditure, name='bin_expenditure'),
    path('recover_expenditure', expenditure_views.recover_expenditure, name='recover_expenditure'),
    path('update_expenditure/<int:id>', expenditure_views.update_expenditure, name='update_expenditure'),
    path('delete_expenditure', expenditure_views.delete_expenditure, name="delete_expenditure"),
    path('expenditure_bin/', expenditure_views.binned_expenditure_list, name='expenditure_bin'),
    path('filter_title/', expenditure_views.filter_by_title, name='filter_title'),
    path('filter_category/', expenditure_views.filter_by_category, name='filter_category'),
    path('filter_miscellaneous/', expenditure_views.filter_by_miscellaneous, name='filter_miscellaneous'),

    #paths concerning challenges/achievements
    path('challenge_list/', views.challenge_list, name='challenge_list'),
    path('challenge_details/<int:id>/', views.challenge_details, name='challenge_details'),
    path('enter_challenge/', views.enter_challenge, name='enter_challenge'),
    path('my_challenges/', views.my_challenges, name='my_challenges'),
    path('share_challenge/<int:id>', views.share_challenge, name='share_challenge'),
    path('handle_share/', views.handle_share, name='handle_share'),
    path('achievement_list/', views.achievement_list, name='achievement_list'),
    path('my_achievements/', views.my_achievements, name='my_achievements'),
    path('share_achievement/<int:id>', views.share_achievement, name='share_achievement'),
    path('share/', views.share, name='share'),

    #paths concerning avatars
    path('create_avatar/', views.create_avatar, name='create_avatar'),
    path('share_avatar/', views.share_avatar, name='share_avatar'),
    re_path(r'^my_activity/$', views.my_activity, name='my_activity'),
    re_path(r'^my_avatar/$', views.my_avatar, name='my_avatar'),
    re_path(r'^unlock_avatar/$', views.unlock_avatar, name='unlock_avatar'),

    #paths concerning forum
    path('forum_home/', views.forum_home, name='forum_home'),
    path('posts/', views.posts, name='posts'),
    path('posts/<slug>/', views.posts, name='posts'),
    path('detail/<slug>/', views.detail, name='detail'),
    path('tinymce/', include('tinymce.urls')),
    path('hitcount/', include('hitcount.urls', namespace='hitcount')),
    path('create_post/', views.create_post, name='create_post'),
    path('latest_posts/', views.latest_posts, name='latest_posts'),
    path('search_result/', views.search_result, name ='search_result'),
    path('profile/<int:id>', views.profile, name ='profile'),
    path('delete_post/<int:id>', views.delete_post, name = 'delete_post'),
    path('edit_post/<int:id>', views.edit_post, name = 'edit_post'),
    path('share_post/<int:id>', views.share_post, name = 'share_post'),
    path('delete_comment/<int:id>', views.delete_comment, name = 'delete_comment'),
    path('edit_comment/<int:id>', views.edit_comment, name = 'edit_comment'),
    path('share_comment/<int:id>', views.share_comment, name = 'share_comment'),
    path('delete_reply/<int:id>', views.delete_reply, name = 'delete_reply'),
    path('edit_reply/<int:id>', views.edit_reply, name = 'edit_reply'),
    path('share_reply/<int:id>', views.share_reply, name = 'share_reply'),

    #paths concerning admin
    path('superuser_dashboard/', views.superuser_dashboard, name='superuser_dashboard'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('delete', views.delete, name='delete'),
    path('user_promote', views.user_promote, name ='user_promote'),
    path('user_demote', views.user_demote, name ='user_demote'),
    path('user_table/', views.user_table, name='user_table'),
    path('category_table/', views.category_table, name='category_table'),
    path('challenge_table/', views.challenge_table, name='challenge_table'),
    path('achievement_table/', views.achievement_table, name='achievement_table'),
    ]


if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
