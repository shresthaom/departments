from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from HomePage.views import Home
from patients.views import user_login, user_logout
from .views import role_based_redirect

urlpatterns = [

    # Homepage
path('', user_login, name='home'),
    # Login
    path(
        'login/',
        user_login,
        name='login'
    ),

    # Logout
    path(
        'logout/',
        user_logout,
        name='logout'
    ),

    # Role-based redirect after login
    path(
        'redirect/',
        role_based_redirect,
        name='role_redirect'
    ),

    # Django Admin
    path(
        'django-admin/',
        admin.site.urls
    ),

    # Dashboards
    path(
        'admin-dashboard/',
        include('admin_dashboard.urls')
    ),

    path(
        'patients-dashboard/',
        include('patients.urls')
    ),

    # Apps
    path(
        'patients/',
        include('patients.urls')
    ),

    path(
        'doctors/',
        include('doctors.urls')
    ),

    path(
        'hospitals/',
        include('hospitals.urls')
    ),

    path(
        'appointment/',
        include('appointment.urls')
    ),
    path("payments/", include("payments.urls")),
    

    
]
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
