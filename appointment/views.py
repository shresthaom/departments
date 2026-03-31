from django.shortcuts import render,redirect,get_object_or_404


# Create your views here.

from doctors.models import Doctor
from .models import Appointment
from django.contrib.auth.decorators import login_required

@login_required
def book_appointment(request,doctor_id):
    doctor=get_object_or_404(Doctor,doctor_id=doctor_id)

    if request.method=="POST":
        date=request.POST['date']
        time=request.POST['time']

        Appointment.objects.create(
            patient=request.user,
            doctor=doctor,
            appointment_date=date,
            appointment_time=time
        )

        return redirect('patient_dashboard')
    return render(request, 'appointment/book_appointment.html', {'doctor': doctor})