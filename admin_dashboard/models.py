from django.db import models
from django.contrib.auth.models import User


class AdminProfile(models.Model):
    # link to django auth user
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # extra fields for admin dashboard
    phone = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='admin_profiles/', blank=True, null=True)

    def __str__(self):
        return self.user.username