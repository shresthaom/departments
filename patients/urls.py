from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    path('dashboard/', views.patient_dashboard, name='patient_dashboard'),

    path('appointment/<int:appointment_id>/', views.appointment_detail, name='appointment_detail'),
    path('cancel/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),

    path('register-details/', views.register_patients, name='register_patient_details'),
    path('success/', views.success, name='success'),
]