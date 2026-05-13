from django.shortcuts import render, redirect
from doctors.models import Doctor
from hospitals.models import Hospital
from appointment.models import Appointment
from django.utils import timezone
from appointment.views import get_appt_datetime


def Home(request):

    # redirect doctor users to doctor dashboard
    if request.user.is_authenticated and hasattr(request.user, 'doctor'):
        return redirect('doctor_dashboard')

    # patient homepage logic
    if request.user.is_authenticated:

        appointments = Appointment.objects.filter(patient=request.user)

        past_appointments = []
        upcoming_appointments = []

        now = timezone.now()

        for appt in appointments:

            # skip cancelled appointments
            if appt.status == "cancelled":
                continue

            # split past and upcoming using datetime comparison
            if get_appt_datetime(appt) < now:
                past_appointments.append(appt)
            else:
                upcoming_appointments.append(appt)

    else:
        past_appointments = []
        upcoming_appointments = []

    # homepage context (only relevant for patients/guests)
    context = {
        'past_appointments': past_appointments,
        'past_count': len(past_appointments),
        'upcoming_count': len(upcoming_appointments),
        'upcoming_appointments': upcoming_appointments,

        'doctors': Doctor.objects.all(),
        'hospitals': Hospital.objects.all(),
    }

    return render(request, 'HomePage/homepage.html', context)