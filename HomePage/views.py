from django.shortcuts import render
from doctors.models import Doctor
from hospitals.models import Hospital
from appointment.models import Appointment
from django.utils import timezone
from appointment.views import get_appt_datetime, is_past


def Home(request):

    if request.user.is_authenticated:

        appointments = Appointment.objects.filter(patient=request.user)

        past_appointments = []
        upcoming_appointments = []

        now = timezone.now()

        for appt in appointments:
            if appt.status == "cancelled":
                continue

            if get_appt_datetime(appt) < now:
                past_appointments.append(appt)
            else:
                upcoming_appointments.append(appt)

    else:
        past_appointments = Appointment.objects.none()
        upcoming_appointments = Appointment.objects.none()

    context = {
        'past_appointments': past_appointments,
        'past_count': len(past_appointments),
        'upcoming_count': len(upcoming_appointments),

        'upcoming_appointments': upcoming_appointments,

        'doctors': Doctor.objects.all(),
        'hospitals': Hospital.objects.all(),
    }

    return render(request, 'HomePage/homepage.html', context)