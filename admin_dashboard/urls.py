from django.urls import path
from . import views

urlpatterns = [

    # dashboard
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # api
    path('calendar-events/', views.calendar_events, name='calendar_events'),

    # modules
    path('doctors/', views.admin_doctors, name='admin_doctors'),
    path('patients/', views.admin_patients, name='admin_patients'),
    path('hospitals/', views.admin_hospitals, name='admin_hospitals'),
    path('appointments/', views.admin_appointments, name='admin_appointments'),

    # detail pages
    path('doctor/<int:doctor_id>/', views.doctor_detail, name='doctor_detail'),
    path('patient/<int:user_id>/', views.patient_detail, name='patient_detail'),
    path('hospital/<int:hospital_id>/', views.hospital_detail, name='hospital_detail'),

     # doctor CRUD
    path(
            "doctor/add/",
            views.add_doctor,
            name="add_doctor"
    ),
    
    path(
            "doctor/<int:doctor_id>/edit/",
            views.edit_doctor,
            name="edit_doctor"
    ),
    
    path(
            "doctor/<int:doctor_id>/delete/",
            views.delete_doctor,
            name="delete_doctor"
    ),

    # hospital CRUD

path(
    "hospital/add/",
    views.add_hospital,
    name="add_hospital"
),

path(
    "hospital/<int:hospital_id>/edit/",
    views.edit_hospital,
    name="edit_hospital"
),

path(
    "hospital/<int:hospital_id>/delete/",
    views.delete_hospital,
    name="delete_hospital"
),

    # actions
    path('doctor/toggle/<int:doctor_id>/', views.toggle_doctor, name='toggle_doctor'),


    path("payments/", views.admin_payments, name="admin_payments"),

    path(
        "payments/<int:transaction_id>/",
        views.payment_detail,
        name="payment_detail"
    ),

    path(
        "payments/<int:transaction_id>/mark-paid/",
        views.mark_payment_paid,
        name="mark_payment_paid"
    ),

    path(
        "payments/<int:transaction_id>/mark-unpaid/",
        views.mark_payment_unpaid,
        name="mark_payment_unpaid"
    ),
   

   #receipt

   path(
        "payments/<int:transaction_id>/receipt/",
        views.payment_receipt,
        name="payment_receipt"
    ),

    path(
    "leave-requests/",
    views.admin_leave_requests,
    name="admin_leave_requests",
),
path(
    "leave/<int:leave_id>/approve/",
    views.approve_leave,
    name="approve_leave",
),

path(
    "leave/<int:leave_id>/reject/",
    views.reject_leave,
    name="reject_leave",
),


   path(
    "appointments/<int:appointment_id>/approve/",
    views.admin_approve_appointment,
    name="admin_approve_appointment"
),

path(
    "appointments/<int:appointment_id>/reject/",
    views.admin_reject_appointment,
    name="admin_reject_appointment"
),

path(
    "patient/<int:patient_id>/edit/",
    views.edit_patient,
    name="edit_patient"
),

path(
    "patient/<int:patient_id>/delete/",
    views.delete_patient,
    name="delete_patient"
),

]