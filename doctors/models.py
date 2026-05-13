from django.db import models
from django.contrib.auth.models import User


class Doctor(models.Model):
    doctor_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    name = models.CharField(max_length=100)
    qualification = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)
    experience_years = models.PositiveIntegerField(default=0)

    hospital = models.ForeignKey('hospitals.Hospital', on_delete=models.CASCADE, null=True, blank=True)
    department = models.ForeignKey('hospitals.Department', on_delete=models.CASCADE, null=True, blank=True)

    email = models.EmailField(unique=True)
    fees = models.DecimalField(max_digits=8, decimal_places=2)
    phone = models.CharField(max_length=13)

    a_status = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class DoctorAvailability(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    day_of_week = models.IntegerField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        unique_together = ('doctor', 'day_of_week')

    def __str__(self):
        return f"{self.doctor.name} availability"


class DoctorLeave(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)

    def clean(self):
        from django.core.exceptions import ValidationError

        # skip validation if record is being soft deleted
        if self.is_deleted:
            return

        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                raise ValidationError("end date cannot be before start date")

    def save(self, *args, **kwargs):
        # run validation only when not soft deleting
        if not self.is_deleted:
            self.full_clean()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.doctor.name} leave"