from django.db import models

# Create your models here.

class Appointment(models.Model):
    appointment_id=models.AutoField(primary_key=True)
    appointment_date=models.DateField()
    status=models.CharField(max_length=50)
    