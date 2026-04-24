from django.urls import path
from . import views

urlpatterns = [
    path('', views.hospital_list, name='hospital_list'),
    path('<int:hospital_id>/', views.hospital_detail, name='hospital_detail'),
    path('department/<int:department_id>/', views.department_detail, name='department_detail'),
    path('hospitals/<int:hospital_id>/', views.hospital_detail, name='hospital_detail'),
]