from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Patients(models.Model):
    patient_id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=150)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    email=models.EmailField(blank=True,null=True)
    address=models.CharField(max_length=150)
    phone=models.CharField(max_length=10)
    dob=models.DateField()
    Gender_Choices=[
        ('M','Male'),
        ('F','Female'),
        ('O','Other'),
    ]
    gender=models.CharField(max_length=1,choices=Gender_Choices)