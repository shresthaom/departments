from django.shortcuts import render
from doctors.models import Doctor
from hospitals.models import Hospital
from appointment.models import Appointment
from datetime import date


def Home(request):
    doctors = Doctor.objects.all()
    hospitals = Hospital.objects.all()

    appointment_count = 0

    if request.user.is_authenticated:
        appointment_count = Appointment.objects.filter(
            patient=request.user,
            appointment_date__gte=date.today()
        ).count()

    return render(request, "HomePage/homepage.html", {
        'doctors': doctors,
        'hospitals': hospitals,
        'appointment_count': appointment_count
    })