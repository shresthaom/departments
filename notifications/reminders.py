from datetime import datetime, timedelta

from django.utils import timezone

from appointment.models import Appointment
from patients.models import Patients

from notifications.models import Notification
from notifications.services import (
    create_notification,
    send_notification_email
)
from notifications.sms import send_sms


# send reminders for upcoming appointments
def send_reminders():

    print("REMINDER SERVICE STARTED")

    now = timezone.localtime()

    appointments = Appointment.objects.filter(
        status="upcoming",
        appointment_date__gte=timezone.localdate()
    ).select_related(
        "doctor",
        "patient"
    )

    for appointment in appointments:

        # skip appointments without a patient
        if appointment.patient is None:
            continue

        appointment_datetime = timezone.make_aware(
            datetime.combine(
                appointment.appointment_date,
                appointment.appointment_time
            )
        )

        send_12_hour_reminder(
            appointment,
            appointment_datetime,
            now
        )

        send_2_hour_reminder(
            appointment,
            appointment_datetime,
            now
        )


# send reminder 12 hours before appointment
def send_12_hour_reminder(
    appointment,
    appointment_datetime,
    now
):

    reminder_time = appointment_datetime - timedelta(hours=12)

    # send only between reminder time and appointment time
    if not (
        reminder_time <= now < appointment_datetime
    ):
        return

    notification = Notification.objects.filter(
        appointment=appointment,
        reminder_type="12_hours"
    ).first()

    if notification is None:

        create_notification(

            patient=appointment.patient,

            appointment=appointment,

            title="Appointment Reminder",

            message=(
                f"You have an appointment with "
                f"Dr. {appointment.doctor.name} "
                f"on {appointment.appointment_date} "
                f"at {appointment.appointment_time}."
            ),

            reminder_type="12_hours"

        )

        notification = Notification.objects.get(
            appointment=appointment,
            reminder_type="12_hours"
        )

    # skip if sms already sent
    if notification.sms_12_sent:
        return

    patient = Patients.objects.filter(
        user=appointment.patient
    ).first()

    # skip if patient profile does not exist
    if patient is None:
        return

    send_sms(

        patient.phone,

        (
            f"DocAp Reminder\n\n"
            f"Doctor: Dr. {appointment.doctor.name}\n"
            f"Date: {appointment.appointment_date}\n"
            f"Time: {appointment.appointment_time}\n\n"
            f"Please arrive 10 minutes early."
        )

    )

    notification.sms_12_sent = True
    notification.save()

    try:

        send_notification_email(

            patient=patient,

            subject="ODAS Appointment Reminder",

            message=(

                f"Hello {patient.name},\n\n"

                f"This is a reminder that you have an appointment with "

                f"Dr. {appointment.doctor.name} on "

                f"{appointment.appointment_date} at "

                f"{appointment.appointment_time}.\n\n"

                "Please arrive 10 minutes early.\n\n"

                "Thank you,\n"

                "ODAS"

            )

        )

    except Exception as e:

        print("Email Error:", e)


# send reminder 2 hours before appointment
def send_2_hour_reminder(
    appointment,
    appointment_datetime,
    now
):

    reminder_time = appointment_datetime - timedelta(hours=2)

    # send only between reminder time and appointment time
    if not (
        reminder_time <= now < appointment_datetime
    ):
        return

    notification = Notification.objects.filter(
        appointment=appointment,
        reminder_type="2_hours"
    ).first()

    if notification is None:

        create_notification(

            patient=appointment.patient,

            appointment=appointment,

            title="Appointment Reminder",

            message=(
                f"You have an appointment with "
                f"Dr. {appointment.doctor.name} "
                f"in about 2 hours."
            ),

            reminder_type="2_hours"

        )

        notification = Notification.objects.get(
            appointment=appointment,
            reminder_type="2_hours"
        )

    # skip if sms already sent
    if notification.sms_2_sent:
        return

    patient = Patients.objects.filter(
        user=appointment.patient
    ).first()

    # skip if patient profile does not exist
    if patient is None:
        return

    send_sms(

        patient.phone,

        (
            f"DocAp Reminder\n\n"
            f"You have an appointment with "
            f"Dr. {appointment.doctor.name}\n"
            f"in about 2 hours.\n\n"
            f"Please arrive 10 minutes early."
        )

    )

    notification.sms_2_sent = True
    notification.save()

    try:

        send_notification_email(

            patient=patient,

            subject="ODAS Appointment Reminder",

            message=(

                f"Hello {patient.name},\n\n"

                f"This is a reminder that your appointment with "

                f"Dr. {appointment.doctor.name} "

                f"is in about 2 hours.\n\n"

                f"Appointment Date: {appointment.appointment_date}\n"

                f"Appointment Time: {appointment.appointment_time}\n\n"

                "Please arrive 10 minutes early.\n\n"

                "Thank you,\n"

                "ODAS"

            )

        )

    except Exception as e:

        print("Email Error:", e)