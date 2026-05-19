from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # lists
    path('doctors/', views.admin_doctors, name='admin_doctors'),
    path('patients/', views.admin_patients, name='admin_patients'),
    path('hospitals/', views.admin_hospitals, name='admin_hospitals'),
    path('appointments/', views.admin_appointments, name='admin_appointments'),

    # detail pages (NEW)
    path('doctor/<int:doctor_id>/', views.doctor_detail, name='doctor_detail'),
    path('patient/<int:user_id>/', views.patient_detail, name='patient_detail'),
    path('hospital/<int:hospital_id>/', views.hospital_detail, name='hospital_detail'),
]