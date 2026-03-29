from django.shortcuts import render

from . models import Doctor

# Create your views here.

from django.http import HttpResponse;

docinfos=[
    {
        'name':'Bigyan',
        'qualification':'MBBS',
        'yoe':'14',

    },

    {

        'name':'Bigyan 2',
        'qualification':'MD',
        'yoe':'20',
    }
]

# def DoctorPage(Request):
#     return HttpResponse("<h1> Doctors Page </h1>")

# def DoctorPage(request):
#     context={
#         'docinfos':docinfos
#     }
#     return render(request,'doctors/doctors.html')


def doctor_list(request):
    available=request.GET.get('available')

    if available=='true':
        doctors=Doctor.objects.filter(a_status=True)

    else:
        doctors=Doctor.objects.all()

    return render(request,'doctors/doctors.html',{'doctors':doctors})

