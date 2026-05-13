from django.urls import path
from . import views

urlpatterns = [

    path('', views.doctor_list, name='doctor_list'),
    path('<int:doctor_id>/', views.doctor_detail, name='doctor_detail'),

    path('dashboard/', views.doctor_dashboard, name='doctor_dashboard'),

    path('leave/', views.add_leave, name='add_leave'),
    path('leave/edit/<int:leave_id>/', views.edit_leave, name='edit_leave'),
    path('leave/delete/<int:leave_id>/', views.delete_leave, name='delete_leave'),
    path('set-availability/', views.set_availability, name='set_availability'),

]