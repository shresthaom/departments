from django.shortcuts import render,get_object_or_404

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


from django.shortcuts import render
from .models import Doctor



def doctor_list(request):
    available = request.GET.get('available')

    doctors = Doctor.objects.all()

    if available == 'true':
        doctors = doctors.filter(a_status=True)

    return render(request, 'doctors/doctors.html', {'doctors': doctors})


def doctor_detail(request, doctor_id):
    doctor = get_object_or_404(Doctor, doctor_id=doctor_id)
    return render(request, "doctors/doctor_detail.html", {
        "doctor": doctor
    })