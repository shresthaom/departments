from django.urls import path

from . import views

urlpatterns = [
    path('registerpatientsdetails/',views.register_patients,name="register_patient_details"),
    path('success/',views.success,name="success"),
     path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.patient_dashboard, name='patient_dashboard'),
     
]