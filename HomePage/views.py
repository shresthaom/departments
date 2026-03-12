from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse

def Home(Request):
    return HttpResponse('<h1>Home Page</h1>')


