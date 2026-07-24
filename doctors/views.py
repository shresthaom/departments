from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count
from .models import Doctor, DoctorAvailability, DoctorLeave
from hospitals.models import Hospital
from .forms import DoctorLeaveForm
from appointment.models import Appointment
from .ranking import calculate_score_with_breakdown
from django.http import HttpResponseForbidden
from datetime import datetime, timedelta
from appointment.views import can_update_status
from notifications.services import create_notification
from appointment.utils import update_expired_appointments
# doctor list
def doctor_list(request):

    mode = request.GET.get("mode", "browse")

    hospital_id = request.GET.get("hospital")
    department_id = request.GET.get("department")
    available = request.GET.get("available")
    search = request.GET.get("search")
    specialization = request.GET.get("specialization")

    doctors = Doctor.objects.all()
    if search:
        doctors = doctors.filter(name__icontains=search)
    if specialization:
        doctors = doctors.filter(specialization=specialization)

    if hospital_id:
        doctors = doctors.filter(hospital_id=hospital_id)

    if department_id:
        doctors = doctors.filter(department_id=department_id)

   
    ranked = []

    for doctor in doctors:
        score, breakdown = calculate_score_with_breakdown(doctor)

        ranked.append({
            "doctor": doctor,
            "score": score,
            "breakdown": breakdown
        })

    ranked.sort(key=lambda x: x["score"], reverse=True)

    # assign rank number
    for i, item in enumerate(ranked, start=1):
        item["rank"] = i

    specializations = (
    Doctor.objects
    .values_list("specialization", flat=True)
    .distinct()
)

    hospitals = Hospital.objects.all()

    return render(request, "doctors/doctors.html", {
        "ranked_doctors": ranked,
        "mode": mode,
        "specializations": specializations,
        "hospitals": hospitals,
    })


DAY_NAMES = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday",
}


# doctor detail
def doctor_detail(request, doctor_id):

    doctor = get_object_or_404(Doctor, doctor_id=doctor_id)

    availability = DoctorAvailability.objects.filter(doctor=doctor)


    schedule = []

    for day in range(7):

        slot = availability.filter(day_of_week=day).first()

        if slot:
            schedule.append({
                "day": DAY_NAMES[day],
                "available": True,
                "start": slot.start_time,
                "end": slot.end_time,
            })
        else:
            schedule.append({
                "day": DAY_NAMES[day],
                "available": False,
            })

    return render(
        request,
        "doctors/doctor_detail.html",
        {
            "doctor": doctor,
            "schedule": schedule,
        }
    )

@login_required


def doctor_dashboard(request):

    if not hasattr(request.user, "doctor"):
        return HttpResponseForbidden(
            "Only registered doctors can access this dashboard."
        )

    # Update expired appointments before calculating dashboard statistics
    update_expired_appointments()

    doctor = request.user.doctor
    today = timezone.localdate()

    # Dashboard counts
    today_count = Appointment.objects.filter(
        doctor=doctor,
        appointment_date=today,
        status="upcoming"
    ).count()

    upcoming_appts = Appointment.objects.filter(
        doctor=doctor,
        status="upcoming"
    )

    completed_appts = Appointment.objects.filter(
        doctor=doctor,
        status="completed"
    )

    leaves = DoctorLeave.objects.filter(
        doctor=doctor,
        is_deleted=False
    )

    availability = DoctorAvailability.objects.filter(
        doctor=doctor
    )

    today_availability = availability.filter(
        day_of_week=today.weekday()
    ).first()

    day_names = {
        0: "Monday",
        1: "Tuesday",
        2: "Wednesday",
        3: "Thursday",
        4: "Friday",
        5: "Saturday",
        6: "Sunday",
    }

    week_schedule = []

    for day in range(7):

        slot = availability.filter(
            day_of_week=day
        ).first()

        week_schedule.append({
            "day_number": day,
            "day_name": day_names[day],
            "slot": slot,
        })

    appointment_stats = Appointment.objects.filter(
        doctor=doctor
    ).values("status").annotate(
        total=Count("status")
    )

    status_dict = {
        item["status"]: item["total"]
        for item in appointment_stats
    }

    labels = [
        "upcoming",
        "completed",
        "cancelled",
        "missed"
    ]

    chart_data = [
        status_dict.get(label, 0)
        for label in labels
    ]

    return render(
        request,
        "doctors/dashboard.html",
        {
            "doctor": doctor,
            "completed_count": completed_appts.count(),
            "upcoming_count": upcoming_appts.count(),
            "today_count": today_count,
            "leave_count": leaves.count(),
            "leaves": leaves,
            "availability": availability,
            "today_availability": today_availability,
            "week_schedule": week_schedule,
            "today": today,
            "weekday": today.weekday(),
            "chart_labels": labels,
            "chart_data": chart_data,
        }
    )

@login_required
def doctor_appointments(request):

    if not hasattr(request.user, "doctor"):
        return HttpResponseForbidden(
            "Only registered doctors can access this page."
        )

    doctor = request.user.doctor
    now = timezone.now()

    # Automatically mark expired upcoming appointments as missed
    upcoming = Appointment.objects.filter(
        doctor=doctor,
        status="upcoming"
    )

    for appointment in upcoming:

        appointment_datetime = timezone.make_aware(
            datetime.combine(
                appointment.appointment_date,
                appointment.appointment_time
            )
        ) + timedelta(minutes=10)

        if appointment_datetime <= now:
            appointment.status = "missed"
            appointment.save(update_fields=["status"])

    status = request.GET.get("status")

    appointments = Appointment.objects.filter(
        doctor=doctor
    )

    if status:
        appointments = appointments.filter(status=status)

    appointments = appointments.order_by(
        "-appointment_date",
        "-appointment_time"
    )

    return render(
        request,
        "doctors/appointments.html",
        {
            "appointments": appointments,
            "status": status,
        }
    )

@login_required
def manage_today_appointments(request):

    if not hasattr(request.user, "doctor"):
        return HttpResponseForbidden()

    doctor = request.user.doctor
    today = timezone.localdate()

    appointments = Appointment.objects.filter(
        doctor=doctor,
        appointment_date=today
    ).order_by("appointment_time")

    # Add a flag for each appointment
    for appointment in appointments:
        appointment.can_update = can_update_status(appointment)

    return render(
        request,
        "doctors/manage_today.html",
        {
            "appointments": appointments,
        }
    )
@login_required


def leave_management(request):

    if not hasattr(request.user, "doctor"):
        return HttpResponseForbidden()

    doctor = request.user.doctor

    leaves = DoctorLeave.objects.filter(
        doctor=doctor,
        is_deleted=False
    ).order_by("-start_date")

    return render(
        request,
        "doctors/leave_management.html",
        {
            "leaves": leaves,
            "today": timezone.localdate(),
        }
    )
# add leave
@login_required
def add_leave(request):

    doctor = request.user.doctor

    if request.method == "POST":
        form = DoctorLeaveForm(request.POST)

        if form.is_valid():
            leave = form.save(commit=False)
            leave.doctor = doctor

            overlap = DoctorLeave.objects.filter(
                doctor=doctor,
                is_deleted=False,
                status__in=["pending", "approved"],
                start_date__lte=leave.end_date,
                end_date__gte=leave.start_date
            ).exists()

            if overlap:
                return render(request, "doctors/add_leave.html", {
                    "error": "There is already a pending or approved leave request for the selected dates.",
                    "form": form
                })

            leave.save()
            return redirect("doctor_dashboard")

    else:
        form = DoctorLeaveForm()

    return render(request, "doctors/add_leave.html", {
        "form": form
    })


# edit leave
@login_required
def edit_leave(request, leave_id):

    doctor = request.user.doctor

    leave = get_object_or_404(
        DoctorLeave,
        id=leave_id,
        doctor=doctor
    )

    if request.method == "POST":

        form = DoctorLeaveForm(
            request.POST,
            instance=leave
        )

        if form.is_valid():

            updated_leave = form.save(commit=False)

            overlap = DoctorLeave.objects.filter(
                doctor=doctor,
                is_deleted=False,
                status__in=["pending", "approved"],
                start_date__lte=updated_leave.end_date,
                end_date__gte=updated_leave.start_date,
            ).exclude(
                id=leave.id
            ).exists()

            if overlap:

                return render(
                    request,
                    "doctors/edit_leave.html",
                    {
                        "form": form,
                        "error": (
                            "There is already a pending or approved "
                            "leave request for the selected dates."
                        ),
                    },
                )

            updated_leave.save()

            return redirect("doctor_dashboard")

    else:

        form = DoctorLeaveForm(instance=leave)

    return render(
        request,
        "doctors/edit_leave.html",
        {
            "form": form,
        },
    )


# delete leave (soft delete safe fix)
@login_required
def delete_leave(request, leave_id):

    doctor = request.user.doctor

    leave = get_object_or_404(
        DoctorLeave,
        id=leave_id,
        doctor=doctor,
        is_deleted=False
    )

    # show confirmation page first
    if request.method == "POST":

        leave.is_deleted = True
        leave.save(update_fields=['is_deleted'])

        return redirect("doctor_dashboard")

    return render(request, "doctors/confirm_delete_leave.html", {
        "leave": leave
    })


@login_required
def end_leave_early(request, leave_id):

    if not hasattr(request.user, "doctor"):
        return HttpResponseForbidden()

    doctor = request.user.doctor

    leave = get_object_or_404(
        DoctorLeave,
        id=leave_id,
        doctor=doctor,
        status="approved",
        is_deleted=False,
    )

    today = timezone.localdate()

    if leave.start_date <= today < leave.end_date:

        leave.end_date = today
        leave.save(update_fields=["end_date"])

    return redirect("leave_management")


# set availability
@login_required
def set_availability(request):

    doctor = request.user.doctor

    if request.method == "POST":

        day = request.POST.get("day_of_week")
        start = request.POST.get("start_time")
        end = request.POST.get("end_time")

        DoctorAvailability.objects.update_or_create(
            doctor=doctor,
            day_of_week=day,
            defaults={
                "start_time": start,
                "end_time": end,
            }
        )

        return redirect("doctor_dashboard")   
    return render(request, "doctors/set_availability.html")

#doctor can complete the appoijntment
@login_required
def complete_appointment(request, appointment_id):

    if not hasattr(request.user, "doctor"):
        return HttpResponseForbidden()

    doctor = request.user.doctor

    appointment = get_object_or_404(
        Appointment,
        appointment_id=appointment_id,
        doctor=doctor
    )

    appointment.status = "completed"
    appointment.save()

    create_notification(
        patient=appointment.patient,
        appointment=appointment,
        title="Appointment Completed",
        message=(
            f"Your appointment with "
            f"Dr. {appointment.doctor.name} "
            f"has been completed."
        ),
        notification_type="appointment"
    )

    return redirect("doctor_dashboard")

#when patient misses the appointment, doctor can click the action "missed"
@login_required
def missed_appointment(request, appointment_id):

    if not hasattr(request.user, "doctor"):
        return HttpResponseForbidden()

    doctor = request.user.doctor

    appointment = get_object_or_404(
        Appointment,
        appointment_id=appointment_id,
        doctor=doctor
    )

    appointment.status = "missed"
    appointment.save()

    create_notification(
        patient=appointment.patient,
        appointment=appointment,
        title="Appointment Missed",
        message=(
            f"You missed your appointment with "
            f"Dr. {appointment.doctor.name}."
        ),
        notification_type="appointment"
    )

    return redirect("doctor_dashboard")