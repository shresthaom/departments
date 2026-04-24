from django.db import models
from hospitals.models import Department

class Doctor(models.Model):
    doctor_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    qualification = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)
    hospital = models.ForeignKey('hospitals.Hospital', on_delete=models.CASCADE, null=True, blank=True)

    department = models.ForeignKey('hospitals.Department', on_delete=models.CASCADE, null=True, blank=True)

    email = models.EmailField(unique=True)
    fees = models.DecimalField(max_digits=8, decimal_places=2)
    phone = models.CharField(max_length=10)
    a_status = models.BooleanField(default=True)

    def __str__(self):
        return self.name