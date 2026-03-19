from django.shortcuts import render

# Create your views here.


from django.http import HttpResponse

# def Hospital(Request):
#     return HttpResponse("<h1> Hospital Page</h1>")

def Hospital(request):
    return render(request,'hospitals/hospitals.html')