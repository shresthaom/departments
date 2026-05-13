from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('HomePage.urls')),
    path('', include('patients.urls')),
    path('admin/', admin.site.urls),

    path('homepage/', include('HomePage.urls')),
    path('doctors/', include('doctors.urls')),
    path('hospitals/', include('hospitals.urls')),
    path('appointment/', include('appointment.urls')),
]