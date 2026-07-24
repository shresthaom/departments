from django.db import models
from django.contrib.auth.models import User
from doctors.models import Doctor


class Appointment(models.Model):

    appointment_id = models.AutoField(primary_key=True)

    appointment_date = models.DateField()
    appointment_time = models.TimeField()

    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('missed', 'Missed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    # appointment approval/rejection
    APPROVAL_CHOICES = [
        ("approved", "Approved"),
        ("review", "Needs Review"),
        ("rejected", "Rejected"),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='upcoming'
    )

    approval_status = models.CharField(
        max_length=20,
        choices=APPROVAL_CHOICES,
        default="approved",
    )

    review_reason = models.CharField(
        max_length=255,
        blank=True,
    )

    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ('doctor', 'appointment_date', 'appointment_time')

    def __str__(self):
        return f"{self.patient} - {self.doctor} - {self.appointment_date} {self.appointment_time}"


class MedicalReport(models.Model):

    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE
    )

    diagnosis = models.TextField()

    prescription = models.TextField()

    remarks = models.TextField(
        blank=True
    )

    report_file = models.FileField(
        upload_to="reports/",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Report - {self.appointment.patient.username}"