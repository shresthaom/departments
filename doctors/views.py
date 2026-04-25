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

def calculate_score(doctor):
    score = 0

    if doctor.a_status:
        score += 40

    score += doctor.experience_years * 2

    if "MD" in doctor.qualification:
        score += 20
    elif "MBBS" in doctor.qualification:
        score += 10

    score += max(0, 50 - float(doctor.fees))

    return score

def doctor_list(request):
    available = request.GET.get('available')

    doctors = Doctor.objects.all()

    if available == 'true':
        doctors = doctors.filter(a_status=True)

    # 🔥 ADD THIS LINE (ranking)
    doctors = sorted(doctors, key=lambda d: calculate_score(d), reverse=True)

    return render(request, 'doctors/doctors.html', {'doctors': doctors})

def doctor_detail(request, doctor_id):
    doctor = get_object_or_404(Doctor, doctor_id=doctor_id)
    return render(request, "doctors/doctor_detail.html", {
        "doctor": doctor
    })