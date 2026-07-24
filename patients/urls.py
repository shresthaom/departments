from django.urls import path
from . import views

urlpatterns = [

    # Register
    path('register/', views.register, name='register'),

    # Patient Dashboard
    path('dashboard/', views.patient_dashboard, name='patient_dashboard'),

    # Appointments
    path(
        'appointment/<int:appointment_id>/',
        views.appointment_detail,
        name='appointment_detail'
    ),

    path(
        'cancel/<int:appointment_id>/',
        views.cancel_appointment,
        name='patient_cancel_appointment'
    ),

    # # Patient Details
    # path(
    #     'register-details/',
    #     views.register_patients,
    #     name='register_patient_details'
    # ),

    path(
        'success/',
        views.success,
        name='success'
    ),

    path(
    'appointments/<str:status>/',
    views.appointment_list,
    name='appointment_list'
),

    path(
        "reschedule/<int:appointment_id>/",
        views.reschedule_appointment,
        name="reschedule_appointment",
    ),
    path(
    "notifications/",
    views.all_notifications,
    name="all_notifications"
),
]