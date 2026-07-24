from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from doctors.models import Doctor, DoctorAvailability, DoctorLeave
from appointment.models import Appointment
from datetime import datetime, timedelta
from django.db.models import Q
from notifications.services import create_notification
from .models import MedicalReport
from payments.models import Transaction
from .forms import MedicalReportForm

DAY_NAMES = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday",
}
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


# allow status update only after time 
def can_update_status(appt):
    return True


# check if appointment is past
def is_past(appt):
    return timezone.now() > get_appt_datetime(appt)


# generate slots based on doctor availability
def generate_slots(doctor, selected_date, exclude_appointment=None):
    if not doctor.a_status:
        return []
    
    date_obj = datetime.strptime(
        selected_date,
        "%Y-%m-%d"
    ).date()

    max_booking_date = timezone.localdate() + timedelta(days=60)

    if date_obj > max_booking_date:
        return []

    # check leave range
    on_leave = DoctorLeave.objects.filter(
        doctor=doctor,
        is_deleted=False,
        status="approved",
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
    slot_count = 0

    while start_time < end_time:

        # Don't generate slots beyond doctor's availability
        if start_time >= end_time:
            break

        slots.append(
            start_time.strftime("%H:%M")
        )

        slot_count += 1

        # One consultation = 15 minutes
        start_time += timedelta(minutes=15)

        # After every 4 consultations, add a 20-minute buffer
        if slot_count % 4 == 0:
            start_time += timedelta(minutes=20)

    booked = Appointment.objects.filter(
        doctor=doctor,
        appointment_date=date_obj
    )

    if exclude_appointment:
        booked = booked.exclude(
            appointment_id=exclude_appointment.appointment_id
        )

    booked_slots = [
        appt.appointment_time.strftime("%H:%M")
        for appt in booked
    ]

    available_slots = []

    # Current time + 30 minute booking buffer
    cutoff = timezone.localtime() + timedelta(minutes=30)

    for slot in slots:

        # Skip booked slots
        if slot in booked_slots:
            continue

        slot_datetime = timezone.make_aware(
            datetime.combine(
                date_obj,
                datetime.strptime(slot, "%H:%M").time()
            )
        )

        # If booking today, don't show past slots
        # or slots within the next 30 minutes
        if date_obj == cutoff.date() and slot_datetime < cutoff:
            continue

        available_slots.append(slot)

    return available_slots

# evaluate appt for suspicious 

def evaluate_appointment(doctor, patient, appointment_date, appointment_time):

    # Default
    approval_status = "approved"
    review_reason = ""

    


    # Rule 1: Too many appointments
    

    start_date = appointment_date
    end_date = appointment_date + timedelta(days=7)

    appointment_count = Appointment.objects.filter(
        patient=patient,
        appointment_date__range=(start_date, end_date),
    ).exclude(
        status="cancelled"
    ).count()

    if appointment_count >= 3:
        return (
            "review",
            "High Appointment Frequency"
        )

    
    # Rule 2: Duplicate booking
  

    # Rule 2: Possible duplicate booking within 1 hour

    appointments = Appointment.objects.filter(
        patient=patient,
        doctor=doctor,
        appointment_date=appointment_date,
    ).exclude(
        status="cancelled"
    )

    new_datetime = datetime.combine(
        appointment_date,
        appointment_time
    )

    for appt in appointments:

        existing_datetime = datetime.combine(
            appt.appointment_date,
            appt.appointment_time
        )

        difference = abs(
            (new_datetime - existing_datetime).total_seconds()
        )

        if difference <= 3600:   # 60 minutes

            return (
                "review",
                "Possible Duplicate Booking"
            )

# book appointment
@login_required
def book_appointment(request, doctor_id):

    doctor = get_object_or_404(
        Doctor,
        doctor_id=doctor_id,
        a_status=True
    )

    selected_date = request.GET.get("date")

    time_slots = []
    on_leave = False

    if selected_date:

        date_obj = datetime.strptime(
            selected_date,
            "%Y-%m-%d"
        ).date()

        # Prevent selecting past dates
        if date_obj < timezone.localdate():

            messages.error(
                request,
                "You cannot book an appointment in the past."
            )

            return redirect(
                "book_appointment",
                doctor_id=doctor.doctor_id
            )
        
        #max booking for 60 days in future

        max_booking_date = timezone.localdate() + timedelta(days=60)

        if date_obj > max_booking_date:

            messages.error(
                request,
                "Appointments can only be booked up to 60 days in advance."
            )

            return redirect(
                "book_appointment",
                doctor_id=doctor.doctor_id
            )

        on_leave = DoctorLeave.objects.filter(
        doctor=doctor,
        is_deleted=False,
        status="approved",
        start_date__lte=date_obj,
        end_date__gte=date_obj
        ).exists()

        time_slots = generate_slots(
            doctor,
            selected_date
        )

        if not time_slots:

            if on_leave:

                messages.error(
                    request,
                    "Doctor is on leave on this date. Please choose another date."
                )

            elif DoctorAvailability.objects.filter(
                doctor=doctor,
                day_of_week=date_obj.weekday()
            ).exists():

                messages.error(
                    request,
                    "All appointment slots are booked for this date. Please choose another date."
                )

            else:

                messages.error(
                    request,
                    "Doctor is not available on this day."
                )

    if request.method == "POST":

        appointment_date = request.POST.get("date")
        appointment_time = request.POST.get("time")

        # Check if date and time are selected
        if not appointment_date or not appointment_time:

            messages.error(
                request,
                "Please select date and time."
            )

            return redirect(
                "book_appointment",
                doctor_id=doctor.doctor_id
            )

        appointment_date_obj = datetime.strptime(
            appointment_date,
            "%Y-%m-%d"
        ).date()

        # Prevent booking on past dates
        if appointment_date_obj < timezone.localdate():

            messages.error(
                request,
                "You cannot book an appointment in the past."
            )

            return redirect(
                "book_appointment",
                doctor_id=doctor.doctor_id
            )
        
        max_booking_date = timezone.localdate() + timedelta(days=60)

        if appointment_date_obj > max_booking_date:

            messages.error(
                request,
                "Appointments can only be booked up to 60 days in advance."
            )

            return redirect(
                "book_appointment",
                doctor_id=doctor.doctor_id
            )
        
        # Prevent booking past time on today's date
        appointment_datetime = timezone.make_aware(
            datetime.combine(
                appointment_date_obj,
                datetime.strptime(
                    appointment_time,
                    "%H:%M"
                ).time()
            )
        )

        booking_cutoff = timezone.localtime() + timedelta(minutes=30)

        if appointment_datetime < booking_cutoff:

            messages.error(
                request,
                "Appointments must be booked at least 30 minutes in advance."
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

    availability = []

    for slot in DoctorAvailability.objects.filter(
        doctor=doctor
    ).order_by("day_of_week"):

        availability.append({
            "day": DAY_NAMES[slot.day_of_week],
            "start": slot.start_time,
            "end": slot.end_time,
        })

    return render(
        request,
        "appointment/book_appointment.html",
        {
            "doctor": doctor,
            "time_slots": time_slots,
            "selected_date": selected_date,
            "availability": availability,
            "on_leave": on_leave,
        }
    )
#confirm_appointment

@login_required
def confirm_appointment(request):

    data = request.session.get("appointment_data")

    if not data:
        return redirect("/")

    doctor = get_object_or_404(
        Doctor,
        doctor_id=data["doctor_id"],
        a_status=True
    )

    if request.method == "POST":

        payment_method = request.POST.get("payment_method")

        if payment_method not in ["stripe", "cash"]:

            messages.error(
                request,
                "Please choose a payment method."
            )

            return redirect("confirm_appointment")

        # Parse appointment date and time
        appointment_date = datetime.strptime(
            data["appointment_date"],
            "%Y-%m-%d"
        ).date()

        appointment_time = datetime.strptime(
            data["appointment_time"],
            "%H:%M"
        ).time()

        # Prevent booking in the past
        if appointment_date < timezone.localdate():

            messages.error(
                request,
                "You cannot book an appointment in the past."
            )

            return redirect(
                "book_appointment",
                doctor_id=doctor.doctor_id
            )

        # Prevent booking more than 60 days ahead
        max_booking_date = timezone.localdate() + timedelta(days=60)

        if appointment_date > max_booking_date:

            messages.error(
                request,
                "Appointments can only be booked up to 60 days in advance."
            )

            return redirect(
                "book_appointment",
                doctor_id=doctor.doctor_id
            )

        # Enforce 30-minute booking buffer
        appointment_datetime = timezone.make_aware(
            datetime.combine(
                appointment_date,
                appointment_time
            )
        )

        booking_cutoff = timezone.localtime() + timedelta(minutes=30)

        if appointment_datetime < booking_cutoff:

            messages.error(
                request,
                "Appointments must be booked at least 30 minutes in advance."
            )

            return redirect(
                "book_appointment",
                doctor_id=doctor.doctor_id
            )

        # Check whether the doctor's slot is already booked
        exists = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=appointment_date,
            appointment_time=appointment_time
        ).exclude(
            status="cancelled"
        ).exists()

        if exists:

            messages.error(
                request,
                "This appointment slot has already been booked."
            )

            return redirect(
                "book_appointment",
                doctor_id=doctor.doctor_id
            )

        # Prevent patient from booking two appointments
        # at the same date and time
        patient_conflict = Appointment.objects.filter(
            patient=request.user,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
        ).exclude(
            status="cancelled"
        ).exists()

        if patient_conflict:

            messages.error(
                request,
                "You already have another appointment scheduled at this date and time."
            )

            return redirect(
                "book_appointment",
                doctor_id=doctor.doctor_id,
            )

        # Evaluate appointment
        approval_status, review_reason = evaluate_appointment(
            doctor,
            request.user,
            appointment_date,
            appointment_time,
        )

        # Create appointment
        appointment = Appointment.objects.create(
            doctor=doctor,
            patient=request.user,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            status="upcoming",
            approval_status=approval_status,
            review_reason=review_reason,
        )

        # Create notification
        if approval_status == "approved":

            create_notification(
                patient=request.user,
                appointment=appointment,
                title="Appointment Confirmed",
                message=(
                    f"Your appointment with Dr. {doctor.name} "
                    f"has been confirmed for "
                    f"{appointment.appointment_date} at "
                    f"{appointment.appointment_time}."
                ),
                reminder_type="general",
            )

        else:

            create_notification(
                patient=request.user,
                appointment=appointment,
                title="Appointment Under Review",
                message=(
                    f"Your appointment with Dr. {doctor.name} "
                    f"is under review because: "
                    f"{review_reason}."
                ),
                reminder_type="general",
            )

        # Create payment transaction
        Transaction.objects.create(
            appointment=appointment,
            amount=doctor.fees,
            payment_method=payment_method,
            payment_status="pending",
        )

        # Clear booking session
        del request.session["appointment_data"]

        # Redirect Stripe payments
        if payment_method == "stripe":

            return redirect(
                "stripe_payment",
                appointment_id=appointment.appointment_id,
            )

        # Cash payment messages
        if approval_status == "approved":

            messages.success(
                request,
                "Appointment booked successfully."
            )

        else:

            messages.warning(
                request,
                "Your appointment has been submitted and is awaiting review."
            )

        return redirect("patient_dashboard")

    return render(
        request,
        "appointment/confirm.html",
        {
            "doctor": doctor,
            "data": data,
        }
    )

# patient dashboard
@login_required
def upcoming_appointments(request):

    appointments = Appointment.objects.filter(
        patient=request.user
    )

    now = timezone.localtime()

    upcoming = []
    past = []

    for appt in appointments:

        appt_datetime = get_appt_datetime(appt)

        # Debug prints
        print("NOW:", now)
        print("APPOINTMENT:", appt_datetime)
        print("DATE:", appt.appointment_date)
        print("TIME:", appt.appointment_time)
        print("STATUS:", appt.status)
        print("-------------------------")

        if appt_datetime < now:
            past.append(appt)

        elif appt.status != "cancelled":
            upcoming.append(appt)

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
        print("=" * 40)
        print("TODAY:", timezone.localdate())
        print("NEW DATE:", new_date)
        print("NEW TIME:", new_time)

        

        if not new_date or not new_time:

            messages.error(
                request,
                "Please select date and time."
            )

            return redirect(request.path)

        new_date_obj = datetime.strptime(
            new_date,
            "%Y-%m-%d"
        ).date()

        print("PARSED DATE:", new_date_obj)
        print("IS PAST?:", new_date_obj < timezone.localdate())
        print("=" * 40)

        if new_date_obj < timezone.localdate():

            messages.error(
                request,
                "You cannot reschedule to a past date."
            )

            return redirect(request.path)
        
        max_booking_date = timezone.localdate() + timedelta(days=60)

        if new_date_obj > max_booking_date:

            messages.error(
                request,
                "Appointments can only be rescheduled up to 60 days in advance."
            )

            return redirect(request.path)

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
                "Slot already booked."
            )

            return redirect(request.path)

        appointment.appointment_date = new_date
        appointment.appointment_time = new_time
        appointment.status = "upcoming"

        appointment.save()

        messages.success(
            request,
            "Appointment rescheduled successfully."
        )

        return redirect("doctor_today_appointments")

    today = timezone.localdate()
    max_booking_date = today + timedelta(days=60)

    return render(
        request,
        "appointment/reschedule.html",
        {
            "appointment": appointment,
            "time_slots": time_slots,
            "selected_date": selected_date,
            "today": today.isoformat(),
            "max_booking_date": max_booking_date.isoformat(),
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

@login_required
def upload_report(request, appointment_id):

    if not hasattr(request.user, "doctor"):
        return redirect("login")

    appointment = get_object_or_404(
        Appointment,
        appointment_id=appointment_id,
        doctor=request.user.doctor,
        status="completed",
    )


    if MedicalReport.objects.filter(appointment=appointment).exists():
        return redirect(
            "view_report",
            appointment_id=appointment.appointment_id,
        )

    report = MedicalReport(
        appointment=appointment
    )

    if request.method == "POST":

        form = MedicalReportForm(
            request.POST,
            request.FILES,
            instance=report,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Medical report uploaded successfully."
            )

            return redirect("doctor_appointments")

    else:

        form = MedicalReportForm(instance=report)

    return render(
        request,
        "appointment/upload_report.html",
        {
            "appointment": appointment,
            "form": form,
            "report_exists": False,
        },
    )

from .models import MedicalReport


@login_required
def view_report(request, appointment_id):

    appointment = get_object_or_404(
        Appointment,
        appointment_id=appointment_id,
    )

    report = get_object_or_404(
        MedicalReport,
        appointment=appointment,
    )

    return render(
        request,
        "appointment/view_report.html",
        {
            "appointment": appointment,
            "report": report,
        },
    )

# edit report

@login_required
def edit_report(request, appointment_id):

    if not hasattr(request.user, "doctor"):
        return redirect("login")

    appointment = get_object_or_404(
        Appointment,
        appointment_id=appointment_id,
        doctor=request.user.doctor,
        status="completed",
    )

    report = get_object_or_404(
        MedicalReport,
        appointment=appointment,
    )

    if request.method == "POST":

        form = MedicalReportForm(
            request.POST,
            request.FILES,
            instance=report,
        )

        if form.is_valid():

            form.save()

            create_notification(
                patient=appointment.patient,
                appointment=appointment,
                title="Medical Report Updated",
                message=(
                    f"Your medical report for the appointment on "
                    f"{appointment.appointment_date} has been updated by "
                    f"Dr. {appointment.doctor.name}."
                ),
                reminder_type="general",
            )

            messages.success(
                request,
                "Medical report updated successfully."
            )

            return redirect(
                "view_report",
                appointment_id=appointment.appointment_id,
            )

    else:

        form = MedicalReportForm(
            instance=report
        )

    return render(
        request,
        "appointment/upload_report.html",
        {
            "appointment": appointment,
            "form": form,
            "report_exists": True,
        },
    )

@login_required
def patient_reports(request):

    reports = MedicalReport.objects.filter(
        appointment__patient=request.user
    ).select_related(
        "appointment",
        "appointment__doctor"
    ).order_by("-created_at")

    return render(
        request,
        "appointment/patient_reports.html",
        {
            "reports": reports,
        }
    )