from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from doctors.models import Doctor
from appointment.models import Appointment
from patients.models import Patients


@login_required
def book_appointment(request, doctor_id):
    doctor = get_object_or_404(Doctor, doctor_id=doctor_id)

    if request.method == "POST":
        appointment_date = request.POST.get("appointment_date")
        appointment_time = request.POST.get("appointment_time")
        reason = request.POST.get("reason")

        # store temporarily in session (for confirm page)
        request.session["appointment_data"] = {
            "doctor_id": doctor.doctor_id,
            "appointment_date": appointment_date,
            "appointment_time": appointment_time,
            "reason": reason,
        }

        return redirect("confirm_appointment")

    return render(request, "appointment/book.html", {"doctor": doctor})


@login_required
def confirm_appointment(request):
    data = request.session.get("appointment_data")

    if not data:
        return redirect("/")

    doctor = get_object_or_404(Doctor, doctor_id=data["doctor_id"])

    if request.method == "POST":
        Appointment.objects.create(
            doctor=doctor,
            patient=request.user,
            appointment_date=data["appointment_date"],
            appointment_time=data["appointment_time"],
            status="upcoming"
        )

        del request.session["appointment_data"]

        messages.success(request, "Appointment booked successfully! Redirecting to homepage...")

        return redirect("home")

    return render(request, "appointment/confirm.html", {
        "doctor": doctor,
        "data": data
    })


@login_required
def upcoming_appointments(request):
    appointments = Appointment.objects.filter(
        patient=request.user,
        appointment_date__gte=timezone.now().date()
    ).order_by('appointment_date', 'appointment_time')

    return render(request, "appointment/upcoming.html", {
        "appointments": appointments
    })