from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse

def About(request):
    return HttpResponse('<h1> About Us </h1>')
