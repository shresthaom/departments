from .models import Doctor


def doctor_context(request):
    if request.user.is_authenticated:
        try:
            doctor = Doctor.objects.get(user=request.user)
            return {"doctor": doctor}
        except Doctor.DoesNotExist:
            pass

    return {}