from django.db import models
from django.contrib.auth.models import User
from doctors.models import Doctor

# Create your models here.

class Appointment(models.Model):
    appointment_id=models.AutoField(primary_key=True)
    appointment_date=models.DateField()
    appointment_time=models.TimeField(default="00:00:00")
    status=models.CharField(max_length=50,default="Pending")

    patient=models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    doctor=models.ForeignKey(Doctor,on_delete=models.CASCADE)
    