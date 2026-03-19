from django.db import models

# Create your models here.

class Admin(models.Model):
    admin_id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=100)
    email=models.EmailField(default=True)