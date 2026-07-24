from .models import Notification
from django.core.mail import send_mail
from django.conf import settings


def create_notification(

    patient,

    title,

    message,

    appointment=None,

    notification_type="appointment",

    reminder_type="general"

):

    Notification.objects.create(

        patient=patient,

        appointment=appointment,

        notification_type=notification_type,

        reminder_type=reminder_type,

        title=title,

        message=message

    )

def send_notification_email(

    patient,

    subject,

    message

):

    # don't send if user or email is missing
    if not patient.user or not patient.user.email:
        return

    send_mail(

        subject,

        message,

        settings.DEFAULT_FROM_EMAIL,

        [patient.user.email],

        fail_silently=False

    )