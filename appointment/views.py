from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from doctors.models import Doctor
from appointment.models import Appointment
from datetime import datetime, timedelta


# get full datetime of appointment (timezone aware safe)
def get_appt_datetime(appt):
    naive_dt = datetime.combine(appt.appointment_date, appt.appointment_time)
    return timezone.make_aware(naive_dt, timezone.get_current_timezone())


# check if appointment time is already past
def is_past(appt):
    return timezone.now() > get_appt_datetime(appt) + timedelta(minutes=15)


# book appointment
@login_required
def book_appointment(request, doctor_id):

    doctor = get_object_or_404(Doctor, doctor_id=doctor_id)

    selected_date = request.GET.get("date")
    time_slots = []

    if selected_date:

        # block saturday
        date_obj = datetime.strptime(selected_date, "%Y-%m-%d").date()
        if date_obj.weekday() == 5:
            messages.error(request, "hospitals are closed on saturday.")
            return redirect(request.path)

        start_time = datetime.strptime("09:00", "%H:%M")
        end_time = datetime.strptime("17:00", "%H:%M")

        slots = []
        while start_time <= end_time:
            slots.append(start_time.strftime("%H:%M"))
            start_time += timedelta(minutes=15)

        booked = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=selected_date
        ).values_list('appointment_time', flat=True)

        booked_slots = [t.strftime("%H:%M") for t in booked]
        time_slots = [s for s in slots if s not in booked_slots]

    if request.method == "POST":

        date_str = request.POST.get("date")
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()

        # block saturday booking
        if date_obj.weekday() == 5:
            messages.error(request, "cannot book appointments on saturday.")
            return redirect("book_appointment", doctor_id=doctor.doctor_id)

        request.session["appointment_data"] = {
            "doctor_id": doctor.doctor_id,
            "appointment_date": date_str,
            "appointment_time": request.POST.get("time"),
        }

        return redirect("confirm_appointment")

    return render(request, "appointment/book_appointment.html", {
        "doctor": doctor,
        "time_slots": time_slots,
        "selected_date": selected_date
    })


# confirm appointment
@login_required
def confirm_appointment(request):

    data = request.session.get("appointment_data")
    if not data:
        return redirect("/")

    doctor = get_object_or_404(Doctor, doctor_id=data["doctor_id"])

    if request.method == "POST":

        exists = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=data["appointment_date"],
            appointment_time=data["appointment_time"]
        ).exists()

        if exists:
            messages.error(request, "slot already booked.")
            return redirect("book_appointment", doctor_id=doctor.doctor_id)

        Appointment.objects.create(
            doctor=doctor,
            patient=request.user,
            appointment_date=data["appointment_date"],
            appointment_time=data["appointment_time"],
            status="upcoming"
        )

        del request.session["appointment_data"]

        messages.success(request, "appointment booked successfully.")
        return redirect("upcoming_appointments")

    return render(request, "appointment/confirm.html", {
        "doctor": doctor,
        "data": data
    })


# dashboard
@login_required
def upcoming_appointments(request):

    appointments = Appointment.objects.filter(patient=request.user)

    now = timezone.now()

    upcoming = []
    past = []

    for appt in appointments:
        appt_dt = get_appt_datetime(appt)

        if appt_dt >= now and appt.status != "cancelled":
            upcoming.append(appt)
        else:
            past.append(appt)

    # sort nearest first
    upcoming.sort(key=lambda x: get_appt_datetime(x))
    past.sort(key=lambda x: get_appt_datetime(x), reverse=True)

    return render(request, "appointment/upcoming.html", {
        "upcoming": upcoming,
        "past": past,
    })


# mark completed (user decides)
@login_required
def mark_completed(request, appointment_id):

    appt = get_object_or_404(
        Appointment,
        appointment_id=appointment_id,
        patient=request.user
    )

    if is_past(appt):
        appt.status = "completed"
        appt.save()
    else:
        messages.error(request, "cannot mark future appointment as completed.")

    return redirect("upcoming_appointments")


# reschedule appointment
@login_required
def reschedule_appointment(request, appointment_id):

    appointment = get_object_or_404(
        Appointment,
        appointment_id=appointment_id,
        patient=request.user
    )

    doctor = appointment.doctor
    selected_date = request.GET.get("date")
    time_slots = []

    if selected_date:

        date_obj = datetime.strptime(selected_date, "%Y-%m-%d").date()
        if date_obj.weekday() == 5:
            messages.error(request, "saturday is not available.")
            return redirect(request.path)

        start_time = datetime.strptime("09:00", "%H:%M")
        end_time = datetime.strptime("17:00", "%H:%M")

        slots = []
        while start_time <= end_time:
            slots.append(start_time.strftime("%H:%M"))
            start_time += timedelta(minutes=15)

        booked = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=selected_date
        ).exclude(appointment_id=appointment_id)

        booked_slots = [b.appointment_time.strftime("%H:%M") for b in booked]
        time_slots = [s for s in slots if s not in booked_slots]

    if request.method == "POST":

        new_date = request.POST.get("date")
        date_obj = datetime.strptime(new_date, "%Y-%m-%d").date()

        if date_obj.weekday() == 5:
            messages.error(request, "cannot reschedule to saturday.")
            return redirect(request.path)

        new_time = request.POST.get("time")

        exists = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=new_date,
            appointment_time=new_time
        ).exclude(appointment_id=appointment_id).exists()

        if exists:
            messages.error(request, "slot already booked.")
            return redirect(request.path)

        appointment.appointment_date = new_date
        appointment.appointment_time = new_time
        appointment.status = "upcoming"
        appointment.save()

        messages.success(request, "appointment rescheduled successfully.")
        return redirect("upcoming_appointments")

    return render(request, "appointment/reschedule.html", {
        "appointment": appointment,
        "time_slots": time_slots,
        "selected_date": selected_date
    })

@login_required
def cancel_appointment(request, appointment_id):
    appt = get_object_or_404(
        Appointment,
        appointment_id=appointment_id,
        patient=request.user
    )

    appt.status = "cancelled"
    appt.save()

    messages.success(request, "Appointment cancelled successfully.")
    return redirect("upcoming_appointments")