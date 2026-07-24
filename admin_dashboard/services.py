from django.utils import timezone
from datetime import timedelta
from django.db.models import Count

from doctors.models import Doctor, DoctorLeave
from appointment.models import Appointment
from hospitals.models import Hospital, Department
from django.contrib.auth.models import User


# get analytics data
def get_analytics():
    today = timezone.now().date()
    last_week = today - timedelta(days=7)

    total = Appointment.objects.count()
    weekly = Appointment.objects.filter(appointment_date__gte=last_week).count()

    prev_week = Appointment.objects.filter(
        appointment_date__range=[last_week - timedelta(days=7), last_week]
    ).count()

    growth = ((weekly - prev_week) / prev_week * 100) if prev_week else 0

    return {
        "total_appointments": total,
        "weekly_appointments": weekly,
        "growth": round(growth, 2)
    }


# today panel
def get_today_panel():
    today = timezone.now().date()

    return {
        "today_total": Appointment.objects.filter(appointment_date=today).count(),
        "today_completed": Appointment.objects.filter(appointment_date=today, status='completed').count(),
        "today_cancelled": Appointment.objects.filter(appointment_date=today, status='cancelled').count(),
        "today_missed": Appointment.objects.filter(appointment_date=today, status='missed').count(),
    }


# alerts system
def get_alerts():
    alerts = []

    cancelled = Appointment.objects.filter(status='cancelled').count()
    if cancelled > 20:
        alerts.append("high cancellation rate detected")

    inactive = Doctor.objects.filter(a_status=False).count()
    if inactive > 5:
        alerts.append("multiple inactive doctors")

    no_login = Doctor.objects.filter(user__last_login__isnull=True).count()
    if no_login > 0:
        alerts.append("some doctors never logged in")

    return alerts


# user activity
def get_user_activity():
    last_week = timezone.now() - timedelta(days=7)

    return {
        "total_users": User.objects.count(),
        "new_users": User.objects.filter(date_joined__gte=last_week).count()
    }


# system health
def get_system_health():
    return {
        "system_status": "running",
        "total_doctors": Doctor.objects.count(),
        "total_hospitals": Hospital.objects.count(),
        "total_departments": Department.objects.count()
    }


# calendar events
def get_calendar_events():
    events = []

    for appt in Appointment.objects.all():
        events.append({
            "title": str(appt.patient),
            "start": str(appt.appointment_date),
        })

    return events