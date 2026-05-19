from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from doctors.models import Doctor, DoctorAvailability, DoctorLeave
from appointment.models import Appointment

from datetime import datetime, timedelta
from django.db.models import Q


# get full datetime
def get_appt_datetime(appt):
    naive_dt = datetime.combine(
        appt.appointment_date,
        appt.appointment_time
    )

    return timezone.make_aware(
        naive_dt,
        timezone.get_current_timezone()
    )


# allow status update only after time + 10 min buffer
def can_update_status(appt):
    return timezone.now() >= (
        get_appt_datetime(appt) + timedelta(minutes=10)
    )


# check if appointment is past
def is_past(appt):
    return timezone.now() > get_appt_datetime(appt)


# generate slots based on doctor availability
def generate_slots(doctor, selected_date):

    date_obj = datetime.strptime(
        selected_date,
        "%Y-%m-%d"
    ).date()

    # check leave range
    on_leave = DoctorLeave.objects.filter(
        doctor=doctor,
        is_deleted=False,
        start_date__lte=date_obj,
        end_date__gte=date_obj
    ).exists()

    if on_leave:
        return []

    day = date_obj.weekday()

    availability = DoctorAvailability.objects.filter(
        doctor=doctor,
        day_of_week=day
    ).first()

    if not availability:
        return []

    start_time = datetime.combine(
        date_obj,
        availability.start_time
    )

    end_time = datetime.combine(
        date_obj,
        availability.end_time
    )

    slots = []

    while start_time < end_time:
        slots.append(start_time.strftime("%H:%M"))
        start_time += timedelta(minutes=15)

    booked = Appointment.objects.filter(
        doctor=doctor,
        appointment_date=date_obj
    ).values_list(
        'appointment_time',
        flat=True
    )

    booked_slots = [
        t.strftime("%H:%M")
        for t in booked
    ]

    return [
        s for s in slots
        if s not in booked_slots
    ]


# book appointment
@login_required
def book_appointment(request, doctor_id):

    doctor = get_object_or_404(
        Doctor,
        doctor_id=doctor_id
    )

    selected_date = request.GET.get("date")

    time_slots = []

    if selected_date:

        time_slots = generate_slots(
            doctor,
            selected_date
        )

        if not time_slots:
            messages.error(
                request,
                "doctor not available on this date"
            )

    if request.method == "POST":

        appointment_date = request.POST.get("date")
        appointment_time = request.POST.get("time")

        if not appointment_date or not appointment_time:
            messages.error(
                request,
                "please select date and time"
            )

            return redirect(
                "book_appointment",
                doctor_id=doctor.doctor_id
            )

        request.session["appointment_data"] = {
            "doctor_id": doctor.doctor_id,
            "appointment_date": appointment_date,
            "appointment_time": appointment_time,
        }

        return redirect("confirm_appointment")

    return render(
        request,
        "appointment/book_appointment.html",
        {
            "doctor": doctor,
            "time_slots": time_slots,
            "selected_date": selected_date
        }
    )


# confirm appointment
@login_required
def confirm_appointment(request):

    data = request.session.get("appointment_data")

    if not data:
        return redirect("/")

    doctor = get_object_or_404(
        Doctor,
        doctor_id=data["doctor_id"]
    )

    if request.method == "POST":

        exists = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=data["appointment_date"],
            appointment_time=data["appointment_time"]
        ).exists()

        if exists:

            messages.error(
                request,
                "slot already booked"
            )

            return redirect(
                "book_appointment",
                doctor_id=doctor.doctor_id
            )

        Appointment.objects.create(
            doctor=doctor,
            patient=request.user,
            appointment_date=data["appointment_date"],
            appointment_time=data["appointment_time"],
            status="upcoming"
        )

        del request.session["appointment_data"]

        messages.success(
            request,
            "appointment booked successfully"
        )

        return redirect("upcoming_appointments")

    return render(
        request,
        "appointment/confirm.html",
        {
            "doctor": doctor,
            "data": data
        }
    )


# patient dashboard
@login_required
def upcoming_appointments(request):

    appointments = Appointment.objects.filter(
        patient=request.user
    )

    now = timezone.now()

    upcoming = []
    past = []

    for appt in appointments:

        if (
            get_appt_datetime(appt) >= now
            and appt.status != "cancelled"
        ):
            upcoming.append(appt)

        else:
            past.append(appt)

    upcoming.sort(
        key=lambda x: get_appt_datetime(x)
    )

    past.sort(
        key=lambda x: get_appt_datetime(x),
        reverse=True
    )

    return render(
        request,
        "appointment/upcoming.html",
        {
            "upcoming": upcoming,
            "past": past,
        }
    )


# doctor marks completed
@login_required
def doctor_mark_completed(request, appointment_id):

    if not hasattr(request.user, 'doctor'):
        return redirect('home')

    appt = get_object_or_404(
        Appointment,
        appointment_id=appointment_id,
        doctor=request.user.doctor
    )

    if can_update_status(appt):

        appt.status = "completed"
        appt.save()

    else:

        messages.error(
            request,
            "cannot update before appointment time"
        )

    return redirect("doctor_today_appointments")


# doctor marks missed
@login_required
def doctor_mark_missed(request, appointment_id):

    if not hasattr(request.user, 'doctor'):
        return redirect('home')

    appt = get_object_or_404(
        Appointment,
        appointment_id=appointment_id,
        doctor=request.user.doctor
    )

    if can_update_status(appt):

        appt.status = "missed"
        appt.save()

    else:

        messages.error(
            request,
            "cannot update before appointment time"
        )

    return redirect("doctor_today_appointments")


# doctor reschedules
@login_required
def doctor_reschedule(request, appointment_id):

    if not hasattr(request.user, 'doctor'):
        return redirect('home')

    appointment = get_object_or_404(
        Appointment,
        appointment_id=appointment_id,
        doctor=request.user.doctor
    )

    doctor = appointment.doctor

    selected_date = request.GET.get("date")

    time_slots = []

    if selected_date:

        time_slots = generate_slots(
            doctor,
            selected_date
        )

    if request.method == "POST":

        new_date = request.POST.get("date")
        new_time = request.POST.get("time")

        exists = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=new_date,
            appointment_time=new_time
        ).exclude(
            appointment_id=appointment_id
        ).exists()

        if exists:

            messages.error(
                request,
                "slot already booked"
            )

            return redirect(request.path)

        appointment.appointment_date = new_date
        appointment.appointment_time = new_time
        appointment.status = "upcoming"

        appointment.save()

        messages.success(
            request,
            "appointment rescheduled"
        )

        return redirect("doctor_today_appointments")

    return render(
        request,
        "appointment/reschedule.html",
        {
            "appointment": appointment,
            "time_slots": time_slots,
            "selected_date": selected_date
        }
    )

@login_required
def cancel_appointment(request, appointment_id):

    appointment = get_object_or_404(
        Appointment,
        appointment_id=appointment_id,
        patient=request.user
    )

    appointment.status = "cancelled"
    appointment.save()

    messages.success(
        request,
        "appointment cancelled"
    )

    return redirect("upcoming_appointments")