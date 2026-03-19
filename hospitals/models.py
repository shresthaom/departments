from django.db import models

# Create your models here.

class Hospital(models.Model):
    hospital_id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=100)
    address=models.CharField(max_length=200)
    phone=models.CharField(max_length=100)
    email=models.EmailField(unique=True)
