from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from doctors.models import Doctor
from appointment.models import Appointment
from patients.models import Patients
from datetime import datetime, timedelta


@login_required


@login_required
def book_appointment(request, doctor_id):
    doctor = get_object_or_404(Doctor, doctor_id=doctor_id)

    selected_date = request.GET.get("date")
    time_slots = []

    if selected_date:
        start_time = datetime.strptime("09:00", "%H:%M")
        end_time = datetime.strptime("17:00", "%H:%M")

        # Generate all slots with 15 mins gap
        slots = []
        while start_time <= end_time:
            slots.append(start_time.strftime("%H:%M"))
            start_time += timedelta(minutes=15)

        # get only booked slots
        booked = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=selected_date
        ).values_list('appointment_time', flat=True)

        booked_slots = [t.strftime("%H:%M") for t in booked]

        # removing booked slots
        time_slots = [slot for slot in slots if slot not in booked_slots]

    if request.method == "POST":
        request.session["appointment_data"] = {
            "doctor_id": doctor.doctor_id,
            "appointment_date": request.POST.get("date"),
            "appointment_time": request.POST.get("time"),
        }
        return redirect("confirm_appointment")

    return render(request, "appointment/book_appointment.html", {
        "doctor": doctor,
        "time_slots": time_slots,
        "selected_date": selected_date
    })

@login_required
def confirm_appointment(request):
    data = request.session.get("appointment_data")

    if not data:
        return redirect("/")

    doctor = get_object_or_404(Doctor, doctor_id=data["doctor_id"])

    if request.method == "POST":

        # check if slot is booked
        exists = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=data["appointment_date"],
            appointment_time=data["appointment_time"]
        ).exists()

        if exists:
            messages.error(request, "This time slot is already booked. Please choose another.")
            return redirect("book_appointment", doctor_id=doctor.doctor_id)

        Appointment.objects.create(
            doctor=doctor,
            patient=request.user,
            appointment_date=data["appointment_date"],
            appointment_time=data["appointment_time"],
            status="upcoming"
        )

        del request.session["appointment_data"]

        messages.success(request, "Appointment booked successfully!")
        return redirect("patient_dashboard")

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