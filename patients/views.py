from django.shortcuts import render, redirect, get_object_or_404
from .models import Patients
from appointment.models import Appointment
from datetime import date
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages


# User Initial Registration
def register(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = User.objects.create_user(username=username, password=password)
        user.save()

        return redirect('login')

    return render(request, 'patients/register.html')


# Login
def user_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('patient_dashboard')

    return render(request, 'patients/login.html')


# Logout
def user_logout(request):
    logout(request)
    return redirect('login')


# Patient Dashboard
@login_required
def patient_dashboard(request):
    try:
        patient = Patients.objects.get(user=request.user)
    except Patients.DoesNotExist:
        return redirect('register_patient_details')

    appointments = Appointment.objects.filter(
        patient=request.user
    ).order_by('appointment_date', 'appointment_time')

    today = date.today()

    upcoming = appointments.filter(appointment_date__gte=today)
    past = appointments.filter(appointment_date__lt=today)

    context = {
        'patient': patient,
        'upcoming': upcoming,
        'past': past,
        'upcoming_count': upcoming.count()
    }

    return render(request, 'patients/patient_dashboard.html', context)


# Appointment Detail
@login_required
def appointment_detail(request, appointment_id):
    appointment = get_object_or_404(
        Appointment,
        appointment_id=appointment_id,
        patient=request.user
    )

    return render(request, 'patients/appointment_detail.html', {
        'appointment': appointment
    })


# Cancel Appointment
@login_required
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(
        Appointment,
        appointment_id=appointment_id,
        patient=request.user
    )

    if request.method == "POST":
        appointment.delete()
        messages.success(request, "Appointment cancelled successfully.")
        return redirect('patient_dashboard')

    return redirect('patient_dashboard')

# Success
def success(request):
    return render(request, 'patients/success.html')


# Additional Patient Details after login/registration 
@login_required
def register_patients(request):
    if request.method == "POST":
        name = request.POST.get('name')
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        dob = request.POST.get('dob')
        gender = request.POST.get('gender')

        Patients.objects.create(
            user=request.user,
            name=name,
            address=address,
            phone=phone,
            dob=dob,
            gender=gender
        )

        return redirect('success')

    return render(request, 'patients/patients_form.html')

