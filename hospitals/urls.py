from django.urls import path
 
from . import views



urlpatterns = [
    path('',views.Hospital,name="hospitals/"),
   
]
