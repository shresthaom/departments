from django.shortcuts import render
from doctors.models import Doctor
from hospitals.models import Hospital, Department
from appointment.models import Appointment
from django.utils import timezone
from appointment.views import get_appt_datetime, is_past
from django.db.models import Q


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

 
    query = request.GET.get('q')
    hospital_id = request.GET.get('hospital')
    department_id = request.GET.get('department')

    doctors = Doctor.objects.all()

    if query:
        doctors = doctors.filter(
            Q(name__icontains=query) |
            Q(specialization__icontains=query) |
            Q(hospital__name__icontains=query) |
            Q(department__name__icontains=query)
        )

    if hospital_id:
        doctors = doctors.filter(hospital__hospital_id=hospital_id)
    if department_id:
        doctors = doctors.filter(department_id=department_id)

    context = {
        'past_appointments': past_appointments,
        'past_count': len(past_appointments),
        'upcoming_count': len(upcoming_appointments),
        'upcoming_appointments': upcoming_appointments,

        'doctors': doctors,
        'hospitals': Hospital.objects.all(),
        'departments': Department.objects.all(),  # needed for dropdown
    }

    return render(request, 'HomePage/homepage.html', context)