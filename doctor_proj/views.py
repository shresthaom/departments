from django.shortcuts import redirect
from doctors.models import Doctor


def role_based_redirect(request):

    user = request.user

    # not logged in
    if not user.is_authenticated:
        return redirect('login')

    # admin users
    if user.is_superuser or user.is_staff:
        return redirect('admin_dashboard')

   
    # doctor users
    if Doctor.objects.filter(user=user).exists():
        return redirect('doctor_dashboard')

    # normal users (patients)
    return redirect('patient_dashboard')