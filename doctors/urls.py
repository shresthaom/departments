from django.urls import path
from . import views

urlpatterns = [

    path('', views.doctor_list, name='doctor_list'),
    path('<int:doctor_id>/', views.doctor_detail, name='doctor_detail'),

    path('dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('leaves/', views.leave_management, name='leave_management'),

    path('leave/', views.add_leave, name='add_leave'),
    path('leave/edit/<int:leave_id>/', views.edit_leave, name='edit_leave'),
    path('leave/delete/<int:leave_id>/', views.delete_leave, name='delete_leave'),
    path(
    "leave/end/<int:leave_id>/",
    views.end_leave_early,
    name="end_leave_early"
    ),  
    path('set-availability/', views.set_availability, name='set_availability'),
    path( "appointments/", views.doctor_appointments, name="doctor_appointments"),
    path("appointments/manage/",views.manage_today_appointments, name="manage_today_appointments"),
    path("appointment/<int:appointment_id>/complete/", views.complete_appointment, name="complete_appointment"),
    path("appointment/<int:appointment_id>/missed/", views.missed_appointment, name="missed_appointment"),

]