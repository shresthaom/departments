from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

from HomePage.views import Home
from .views import role_based_redirect

urlpatterns = [

    # homepage
    path('', Home, name='home'),

    # login (redirect handled manually)
    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='registration/login.html'
        ),
        name='login'
    ),

    # logout
    path(
        'logout/',
        auth_views.LogoutView.as_view(),
        name='logout'
    ),

    # role-based redirect after login
    path('redirect/', role_based_redirect, name='role_redirect'),

    # django admin
    path('django-admin/', admin.site.urls),

    # dashboards
    path('admin-dashboard/', include('admin_dashboard.urls')),
    path('patients-dashboard/', include('patients.urls')),  # we assume this exists

    # apps
    path('patients/', include('patients.urls')),
    path('doctors/', include('doctors.urls')),
    path('hospitals/', include('hospitals.urls')),
    path('appointment/', include('appointment.urls')),
]