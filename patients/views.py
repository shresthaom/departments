import re
from django.shortcuts import render, redirect, get_object_or_404
from .models import Patients
from appointment.models import Appointment
from doctors.models import Doctor
from datetime import date
from notifications.models import Notification
from django.contrib.auth.models import User
from notifications.services import create_notification
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from doctors.ranking import calculate_score_with_breakdown
from appointment.views import generate_slots
from datetime import datetime
from django.utils import timezone
from notifications.services import send_notification_email

# user registration
def register(request):

    if request.method == "POST":

        name = request.POST["name"].strip()
        email = request.POST["email"].strip()
        phone = request.POST["phone"].strip()
        address = request.POST["address"].strip()
        dob = request.POST["dob"]
        gender = request.POST["gender"]

        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]
        dob_date = datetime.strptime(dob, "%Y-%m-%d").date()

        today = date.today()

        age = today.year - dob_date.year - (
            (today.month, today.day) < (dob_date.month, dob_date.day)
        )

        if age < 18 or age > 90:

            messages.error(
                request,
                "Age must be between 18 and 90 years."
            )

            return render(
                request,
                "patients/register.html"
    )
        # validate phone number

        if not re.fullmatch(r"9[678]\d{8}", phone):

            messages.error(
                request,
                "Enter a valid Nepali phone number."
            )

            return render(
                request,
                "patients/register.html"
            )

        # check duplicate phone

        if Patients.objects.filter(phone=phone).exists():

            messages.error(
                request,
                "Phone number is already registered."
            )

            return render(
                request,
                "patients/register.html"
            )
        
        # check duplicate email

        if Patients.objects.filter(email=email).exists():

            messages.error(
                request,
                "Email is already registered."
            )

            return render(
                request,
                "patients/register.html"
            )

        # check password confirmation

        if password != confirm_password:

            messages.error(
                request,
                "Passwords do not match."
            )

            return render(
                request,
                "patients/register.html"
            )

        # password length

        if len(password) < 8:

            messages.error(
                request,
                "Password must be at least 8 characters."
            )

            return render(
                request,
                "patients/register.html"
            )

        # uppercase

        if not re.search(r"[A-Z]", password):

            messages.error(
                request,
                "Password must contain an uppercase letter."
            )

            return render(
                request,
                "patients/register.html"
            )

        # lowercase

        if not re.search(r"[a-z]", password):

            messages.error(
                request,
                "Password must contain a lowercase letter."
            )

            return render(
                request,
                "patients/register.html"
            )

        # number

        if not re.search(r"\d", password):

            messages.error(
                request,
                "Password must contain a number."
            )

            return render(
                request,
                "patients/register.html"
            )

        # special character

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):

            messages.error(
                request,
                "Password must contain a special character."
            )

            return render(
                request,
                "patients/register.html"
            )

        # generate hidden username

        username = f"pt{phone}"

        user = User.objects.create_user(

            username=username,

            email=email,

            password=password

        )

        Patients.objects.create(

            user=user,

            name=name,

            email=email,

            phone=phone,

            address=address,

            dob=dob,

            gender=gender

        )

        login(
            request,
            user
        )

        send_notification_email(

            patient=Patients.objects.get(user=user),

            subject="Welcome to ODAS",

            message=(
                f"Hello {name},\n\n"
                "Welcome to the Online Doctor Appointment System.\n\n"
                "Your account has been created successfully."
            )

        )

        messages.success(
            request,
            "Registration completed successfully."
        )

        return redirect(
            "patient_dashboard"
        )

    return render(
        request,
        "patients/register.html"
    )
# login with role-based redirect

# login with phone number

from django.views.decorators.cache import never_cache

@never_cache
def user_login(request):

    # If the user is already logged in, don't let them access the login page
    if request.user.is_authenticated:

        # Admin
        if request.user.is_superuser or request.user.is_staff:
            return redirect("admin_dashboard")

        # Doctor
        elif Doctor.objects.filter(user=request.user).exists():
            return redirect("doctor_dashboard")

        # Patient
        return redirect("patient_dashboard")

    if request.method == "POST":

        login_id = request.POST["login_id"].strip()
        password = request.POST["password"]

        # Patient login using phone number
        if re.fullmatch(r"9[678]\d{8}", login_id):

            patient = Patients.objects.filter(
                phone=login_id
            ).first()

            if patient is None or patient.user is None:

                messages.error(
                    request,
                    "Phone number is not registered."
                )

                return render(
                    request,
                    "patients/login.html"
                )

            user = authenticate(
                request,
                username=patient.user.username,
                password=password
            )

        # Doctor/Admin login using username
        else:

            user = authenticate(
                request,
                username=login_id,
                password=password
            )

        if user is None:

            messages.error(
                request,
                "Invalid username/phone number or password."
            )

            return render(
                request,
                "patients/login.html"
            )

        login(request, user)

        # Redirect according to role
        if user.is_superuser or user.is_staff:
            return redirect("admin_dashboard")

        elif Doctor.objects.filter(user=user).exists():
            return redirect("doctor_dashboard")

        return redirect("patient_dashboard")

    return render(
        request,
        "patients/login.html"
    )

# logout
def user_logout(request):
    logout(request)
    return redirect('login')


@login_required
def patient_dashboard(request):
    patient = Patients.objects.filter(user=request.user).first()

    if not patient:
        messages.error(
            request,
            "Patient profile not found."
        )
        return redirect("logout")

    appointments = Appointment.objects.filter(
        patient=request.user
    ).order_by('appointment_date', 'appointment_time')

    today = date.today()

    upcoming = appointments.filter(
        appointment_date__gte=today,
        status="upcoming"
    ).order_by(
        "appointment_date",
        "appointment_time"
    )
    upcoming_preview = upcoming
    past = appointments.filter(
        appointment_date__lt=today
    )
    # stats for chart
    completed = appointments.filter(status='completed').count()
    upcoming_count = appointments.filter(status='upcoming').count()
    cancelled = appointments.filter(status='cancelled').count()
    missed = appointments.filter(status='missed').count()
    # -----------------------------------
    # Recommended Doctors
    # -----------------------------------

    recommended = []

    doctors = Doctor.objects.filter(a_status=True)

    for doctor in doctors:

        score, breakdown = calculate_score_with_breakdown(doctor)

        recommended.append({
            "doctor": doctor,
            "score": score,
            "breakdown": breakdown
        })

    recommended.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    recommended = recommended[:3]

    #shows only 3 notifications at dashboard
    notifications = Notification.objects.filter(
    patient=request.user
    ).order_by(
        "-created_at"
    )[:3]

    unread_notifications = Notification.objects.filter(
        patient=request.user,
        is_read=False
    ).count()

    # mark notifications as read

    Notification.objects.filter(
        patient=request.user,
        is_read=False
    ).update(is_read=True)

    return render(request, 'patients/patient_dashboard.html', {
    'patient': patient,
    'upcoming': upcoming,
    'past': past,
    'upcoming_count': upcoming.count(),
    'completed': completed,
    'cancelled': cancelled,
    'missed': missed,
    'recommended': recommended,
    "notifications": notifications,
    "unread_notifications": unread_notifications,
})

# appointment detail
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


# cancel appointment
@login_required
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(
        Appointment,
        appointment_id=appointment_id,
        patient=request.user
    )

    if request.method == "POST":

        if appointment.status == "upcoming":
            appointment.status = "cancelled"
            appointment.save()
            create_notification(
                patient=request.user,
                appointment=appointment,
                title="Appointment Cancelled",
                message=(
                    f"Your appointment with "
                    f"Dr. {appointment.doctor.name} "
                    f"has been cancelled."
                ),
                notification_type="system"
            )

            messages.success(
                request,
                "Appointment cancelled successfully."
            )
        else:
            messages.warning(
                request,
                "This appointment cannot be cancelled."
            )

    return redirect("patient_dashboard")

# success page
def success(request):
    return render(request, 'patients/success.html')

# # extra patient details
# @login_required
# def register_patients(request):
#     if request.method == "POST":
#         name = request.POST.get('name')
#         address = request.POST.get('address')
#         phone = request.POST.get('phone')
#         dob = request.POST.get('dob')
#         gender = request.POST.get('gender')

#         Patients.objects.create(
#             user=request.user,
#             name=name,
#             address=address,
#             phone=phone,
#             dob=dob,
#             gender=gender
#         )

#         messages.success(request, "Patient details registered successfully.")
#         return redirect('patient_dashboard')

#     return render(request, 'patients/patients_form.html')


# Appointment list by status
from django.utils import timezone
from appointment.models import Appointment

@login_required
def appointment_list(request, status):

    appointments = Appointment.objects.filter(
        patient=request.user,
        status=status
    ).select_related(
        "doctor",
        "doctor__hospital"
    ).order_by(
        "appointment_date",
        "appointment_time"
    )

    # Automatically update expired upcoming appointments
    if status == "upcoming":

        now = timezone.localtime()

        valid_appointments = []

        for appt in appointments:

            appt_datetime = get_appt_datetime(appt)

            if appt_datetime < now:
                appt.status = "missed"
                appt.save()
            else:
                valid_appointments.append(appt)

        appointments = valid_appointments

    return render(
        request,
        "patients/appointment_list.html",
        {
            "appointments": appointments,
            "status": status.title()
        }
    )
@login_required
def reschedule_appointment(request, appointment_id):

    appointment = get_object_or_404(
        Appointment,
        appointment_id=appointment_id,
        patient=request.user
    )

    slots = []

    selected_date = request.GET.get("date")

    if not selected_date:
        selected_date = appointment.appointment_date.strftime("%Y-%m-%d")

    if selected_date:
        slots = generate_slots(
            appointment.doctor,
            selected_date,
            exclude_appointment=appointment
        )

        if not slots:
            messages.error(
                request,
                "Doctor is not available on the selected date. Please choose another date."
            )

    if request.method == "POST":

        appointment_date = request.POST.get("appointment_date")
        appointment_time = request.POST.get("appointment_time")

        # Prevent rescheduling to a past date
        appointment_date_obj = datetime.strptime(
            appointment_date,
            "%Y-%m-%d"
        ).date()

        if appointment_date_obj < timezone.localdate():
            messages.error(
                request,
                "You cannot reschedule to a past date."
            )

            return redirect(
                "reschedule_appointment",
                appointment_id=appointment.appointment_id
            )

        slots = generate_slots(
            appointment.doctor,
            appointment_date,
            exclude_appointment=appointment
        )

        if not appointment_time or appointment_time not in slots:
            messages.error(
                request,
                "Selected time is not available."
            )

            return redirect(
                "reschedule_appointment",
                appointment_id=appointment.appointment_id
            )

        appointment.appointment_date = appointment_date
        appointment.appointment_time = appointment_time
        appointment.status = "upcoming"
        appointment.save()

        # Notify patient
        create_notification(
            patient=request.user,
            appointment=appointment,
            title="Appointment Rescheduled",
            message=(
                f"Your appointment with "
                f"Dr. {appointment.doctor.name} "
                f"has been rescheduled to "
                f"{appointment.appointment_date} at "
                f"{appointment.appointment_time}."
            ),
            notification_type="appointment"
        )

        messages.success(
            request,
            "Appointment rescheduled successfully."
        )

        return redirect("patient_dashboard")

    return render(
        request,
        "patients/reschedule_appointment.html",
        {
            "appointment": appointment,
            "slots": slots,
            "selected_date": selected_date,
        }
    )

def get_appt_datetime(appt):
    naive_dt = datetime.combine(
        appt.appointment_date,
        appt.appointment_time
    )

    return timezone.make_aware(
        naive_dt,
        timezone.get_current_timezone()
    )

@login_required
def all_notifications(request):

    notifications = Notification.objects.filter(
        patient=request.user
    ).order_by(
        "-created_at"
    )

    return render(
        request,
        "patients/all_notifications.html",
        {
            "notifications": notifications
        }
    )