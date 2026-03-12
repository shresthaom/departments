from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse

#Learning phase

# def Home(Request):
#     return HttpResponse('<h1>Home Page</h1>')

#Advanced trick to render html

def Home(request):
    return render(request,'HomePage/homepage.html')
