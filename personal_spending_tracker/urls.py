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
from django.urls.conf import include  
from django.conf import settings  
from django.conf.urls.static import static  


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('log_out/', views.log_out, name='log_out'),
    path('sign_up/', views.sign_up, name='sign_up'),
    path('landing_page/', views.landing_page, name='landing_page'),
    path('expenditure_list', views.expenditure_list, name='expenditure_list'),
    path('create_expenditure/', views.create_expenditure, name='create_expenditure' ),
    path('challenge_list/', views.challenge_list, name='challenge_list'),
    path('challenge_details/<int:id>/', views.challenge_details, name='challenge_details'),
    path('enter_challenge/', views.enter_challenge, name='enter_challenge'),
    path('my_challenges/', views.my_challenges, name='my_challenges'),
]


if settings.DEBUG:  
        urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)  
