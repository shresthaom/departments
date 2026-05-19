from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth.models import User

from doctors.models import Doctor, DoctorLeave
from django.shortcuts import render, get_object_or_404, redirect
from appointment.models import Appointment
from hospitals.models import Hospital, Department


# admin dashboard home
@login_required
def admin_dashboard(request):

    today = timezone.now().date()

    # appointment stats
    today_appointments = Appointment.objects.filter(appointment_date=today).count()
    upcoming_appointments = Appointment.objects.filter(appointment_date__gt=today).count()

    completed_appointments = Appointment.objects.filter(status='completed').count()
    cancelled_appointments = Appointment.objects.filter(status='cancelled').count()
    missed_appointments = Appointment.objects.filter(status='missed').count()

    total_appointments = Appointment.objects.count()

    # doctor stats
    total_doctors = Doctor.objects.count()
    active_doctors = Doctor.objects.filter(a_status=True).count()

    # patient stats
    total_patients = Appointment.objects.values('patient').distinct().count()

    # hospital stats
    total_hospitals = Hospital.objects.count()
    total_departments = Department.objects.count()

    # leave stats
    doctors_on_leave = DoctorLeave.objects.filter(
        start_date__lte=today,
        end_date__gte=today,
        is_deleted=False
    ).count()

    context = {
        # appointments
        "today_appointments": today_appointments,
        "upcoming_appointments": upcoming_appointments,
        "completed_appointments": completed_appointments,
        "cancelled_appointments": cancelled_appointments,
        "missed_appointments": missed_appointments,
        "total_appointments": total_appointments,

        # doctors
        "total_doctors": total_doctors,
        "active_doctors": active_doctors,
        "doctors_on_leave": doctors_on_leave,

        # patients
        "total_patients": total_patients,

        # hospitals
        "total_hospitals": total_hospitals,
        "total_departments": total_departments,

        # recent
        "recent_doctors": Doctor.objects.order_by('-doctor_id')[:5],
        "recent_appointments": Appointment.objects.order_by('-appointment_id')[:5],
    }

    return render(request, "admin_dashboard/dashboard.html", context)


# doctors page
@login_required
def admin_doctors(request):

    doctors = Doctor.objects.all()
    filter_type = request.GET.get("filter")

    if filter_type == "active":
        doctors = doctors.filter(a_status=True)

    if filter_type == "inactive":
        doctors = doctors.filter(a_status=False)

    if filter_type == "on_leave":
        today = timezone.now().date()
        doctors = doctors.filter(
            doctorleave__start_date__lte=today,
            doctorleave__end_date__gte=today
        ).distinct()

    return render(request, "admin_dashboard/doctors.html", {"doctors": doctors})


# patients page
@login_required

def admin_patients(request):

    # get all users who have at least one appointment
    patient_ids = Appointment.objects.values_list('patient', flat=True).distinct()

    patients = User.objects.filter(id__in=patient_ids)

    return render(request, "admin_dashboard/patients.html", {
        "patients": patients
    })


# hospitals page
@login_required
def admin_hospitals(request):

    hospitals = Hospital.objects.all()

    return render(request, "admin_dashboard/hospitals.html", {"hospitals": hospitals})


# appointments page
@login_required
def admin_appointments(request):

    appointments = Appointment.objects.all()

    status = request.GET.get("status")
    date_filter = request.GET.get("filter")

    if status:
        appointments = appointments.filter(status=status)

    if date_filter == "today":
        today = timezone.now().date()
        appointments = appointments.filter(appointment_date=today)

    return render(request, "admin_dashboard/appointments.html", {
        "appointments": appointments
    })


@login_required
def doctor_detail(request, doctor_id):

    doctor = Doctor.objects.get(doctor_id=doctor_id)

    return render(request, "admin_dashboard/doctor_detail.html", {
        "doctor": doctor
    })


@login_required
def toggle_doctor(request, doctor_id):

    doctor = Doctor.objects.get(doctor_id=doctor_id)
    doctor.a_status = not doctor.a_status
    doctor.save()

    return redirect('admin_doctors')

@login_required
def patient_detail(request, user_id):

    patient = User.objects.get(id=user_id)

    appointments = Appointment.objects.filter(patient_id=user_id)

    return render(request, "admin_dashboard/patient_detail.html", {
        "patient": patient,
        "appointments": appointments
    })


@login_required
def hospital_detail(request, hospital_id):

    hospital = Hospital.objects.get(hospital_id=hospital_id)

    departments = hospital.departments.all()

    return render(request, "admin_dashboard/hospital_detail.html", {
        "hospital": hospital,
        "departments": departments
    })


