from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse;

def DoctorPage(Request):
    return HttpResponse("<h1> Doctors Page </h1>")