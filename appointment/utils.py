from datetime import datetime, timedelta

from django.utils import timezone

from .models import Appointment


def update_expired_appointments():
    now = timezone.now()

    appointments = Appointment.objects.filter(status="upcoming")

    for appointment in appointments:
        appointment_datetime = timezone.make_aware(
            datetime.combine(
                appointment.appointment_date,
                appointment.appointment_time
            )
        ) + timedelta(minutes=10)

        if appointment_datetime <= now:
            appointment.status = "missed"
            appointment.save(update_fields=["status"])