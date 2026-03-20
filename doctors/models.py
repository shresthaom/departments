from django.db import models

# Create your models here.

class Doctor(models.Model):
    doctor_id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=100)
    qualification=models.CharField(max_length=100)
    specialization=models.CharField(max_length=100)
    email=models.EmailField(unique=True)
    fees=models.DecimalField(max_digits=8, decimal_places=2)
    phone=models.CharField(max_length=10)
    a_status=models.BooleanField(default=True)
