from django.db import models
from django.contrib.auth.models import User
from appointment.models import Appointment


class Notification(models.Model):

    TYPE_CHOICES = [
        ("appointment", "Appointment"),
        ("payment", "Payment"),
        ("system", "System"),
    ]

    REMINDER_CHOICES = [
        ("general", "General"),
        ("12_hours", "12 Hours Before"),
        ("2_hours", "2 Hours Before"),
    ]

    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    notification_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default="appointment"
    )

    reminder_type = models.CharField(
        max_length=20,
        choices=REMINDER_CHOICES,
        default="general"
    )

    title = models.CharField(
        max_length=200
    )

    message = models.TextField()

    is_read = models.BooleanField(
        default=False
    )

    sms_12_sent = models.BooleanField(
        default=False
    )

    sms_2_sent = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        ordering = [
            "-created_at"
        ]

    def __str__(self):

        return self.title