from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import Count, Sum, Q
from datetime import timedelta
from django.http import JsonResponse
from payments.models import Transaction
from doctors.models import Doctor, DoctorLeave
from appointment.models import Appointment
from hospitals.models import Hospital, Department
from django.contrib import messages

from patients.models import Patients
from .forms import PatientForm
from notifications.services import create_notification
from .forms import DoctorForm, HospitalForm
from django.db.models.functions import TruncMonth, ExtractYear


# admin dashboard home view
@login_required
def admin_dashboard(request):

    # current date
    today = timezone.now().date()

    # appointment status aggregation
    appointment_stats = Appointment.objects.values('status').annotate(total=Count('status'))

    status_map = {
        "completed": 0,
        "cancelled": 0,
        "missed": 0,
        "upcoming": 0,
    }

    for item in appointment_stats:
        status_map[item['status']] = item['total']

    # basic stats
    today_appointments = Appointment.objects.filter(appointment_date=today).count()
    upcoming_appointments = Appointment.objects.filter(appointment_date__gt=today).count()
    total_appointments = Appointment.objects.count()

    # doctor stats
    total_doctors = Doctor.objects.count()
    active_doctors = Doctor.objects.filter(a_status=True).count()

    # patient stats from appointments
    total_patients = Appointment.objects.values('patient').distinct().count()

    # hospital stats
    total_hospitals = Hospital.objects.count()
    total_departments = Department.objects.count()

    # doctors on leave today
    doctors_on_leave = DoctorLeave.objects.filter(
        start_date__lte=today,
        end_date__gte=today,
        is_deleted=False
    ).count()

    #payment statistics
    completed_payments = Transaction.objects.filter(
        payment_status="completed"
    )

    pending_payments = Transaction.objects.filter(
        payment_status="pending"
    )

    completed_payment_count = completed_payments.count()

    pending_payment_count = pending_payments.count()

    total_revenue = (
        completed_payments.aggregate(
            total=Sum("amount")
        )["total"] or 0
    )



    today = timezone.now().date()

    today_revenue = (
        completed_payments.filter(
            updated_at__date=today
        ).aggregate(
            total=Sum("amount")
        )["total"] or 0
    )


    # Available years that have completed payments
    available_years = (
        Transaction.objects
        .filter(payment_status="completed")
        .annotate(year=ExtractYear("updated_at"))
        .values_list("year", flat=True)
        .distinct()
        .order_by("-year")
    )

    current_year = timezone.now().year

    selected_year = request.GET.get("year")

    if selected_year:
        selected_year = int(selected_year)
    else:
        selected_year = current_year

    # Monthly revenue (completed payments only)
    monthly_data = (
        Transaction.objects
            .filter(
                payment_status="completed",
                updated_at__year=selected_year
            )
            .annotate(month=TruncMonth("updated_at"))
            .values("month")
            .annotate(total=Sum("amount"))
    )   

    month_map = {
        1:0,
        2:0,
        3:0,
        4:0,
        5:0,
        6:0,
        7:0,
        8:0,
        9:0,
        10:0,
        11:0,
        12:0,
    }

    for row in monthly_data:
        month_map[row["month"].month] = float(row["total"])

    month_labels = [
        "Jan","Feb","Mar","Apr",
        "May","Jun","Jul","Aug",
        "Sep","Oct","Nov","Dec"
    ]

    month_totals = list(month_map.values())

    # weekly trend data
    dates = []
    counts = []

    for i in range(7):
        day = today - timedelta(days=i)
        count = Appointment.objects.filter(appointment_date=day).count()
        dates.append(day.strftime("%b %d"))
        counts.append(count)

    dates.reverse()
    counts.reverse()

    # top doctors by appointment count
    top_doctors = Doctor.objects.annotate(
        total=Count('appointment')
    ).order_by('-total')[:5]

    doctor_names = [d.name for d in top_doctors]
    doctor_counts = [d.total for d in top_doctors]

    # recent activity
    recent_doctors = Doctor.objects.order_by('-doctor_id')[:5]
    recent_appointments = Appointment.objects.order_by('-appointment_id')[:5]

    # Payment Method Distribution
    payment_method_data = (
        Transaction.objects
        .values("payment_method")
        .annotate(total=Count("id"))
    )

    payment_method_labels = [
        row["payment_method"].title()
        for row in payment_method_data
    ]

    payment_method_counts = [
        row["total"]
        for row in payment_method_data
    ]


    # Daily Revenue (Last 7 Days)
    daily_labels = []
    daily_totals = []

    for i in range(6, -1, -1):
        day = today - timedelta(days=i)

        total = (
            Transaction.objects.filter(
                payment_status="completed",
                updated_at__date=day
            ).aggregate(
                total=Sum("amount")
            )["total"] or 0
        )

        daily_labels.append(day.strftime("%b %d"))
        daily_totals.append(float(total))

    # context
    context = {
        # cards
        "total_doctors": total_doctors,
        "active_doctors": active_doctors,
        "total_patients": total_patients,
        "total_hospitals": total_hospitals,
        "total_departments": total_departments,
        "total_appointments": total_appointments,

        # today stats
        "today_appointments": today_appointments,
        "upcoming_appointments": upcoming_appointments,
        "doctors_on_leave": doctors_on_leave,

        # status chart
        "completed_appointments": status_map["completed"],
        "cancelled_appointments": status_map["cancelled"],
        "missed_appointments": status_map["missed"],
        "upcoming_status": status_map["upcoming"],

        # charts
        "dates": dates,
        "counts": counts,
        "doctor_names": doctor_names,
        "doctor_counts": doctor_counts,

        # recent
        "recent_doctors": recent_doctors,
        "recent_appointments": recent_appointments,

        #payment stats
        "total_revenue": total_revenue,
        "today_revenue": today_revenue,
        "completed_payments": completed_payment_count,
        "pending_payments": pending_payment_count,

        #payment this month
        "month_labels": month_labels,
        "month_totals": month_totals,

        #payment by year
        "available_years": available_years,
        "selected_year": selected_year,
        "month_labels": month_labels,
        "month_totals": month_totals,

        "payment_method_labels": payment_method_labels,
        "payment_method_counts": payment_method_counts,
        "daily_labels": daily_labels,
        "daily_totals": daily_totals,
    }

    return render(request, "admin_dashboard/dashboard.html", context)


# doctors list page
@login_required
def admin_doctors(request):

    doctors = Doctor.objects.select_related(
        "hospital",
        "department",
        "user"
    ).order_by("name")

    search = request.GET.get("search", "")
    hospital = request.GET.get("hospital", "")
    status = request.GET.get("status", "")

    if search:
        doctors = doctors.filter(
            name__icontains=search
        )

    if hospital:
        doctors = doctors.filter(
            hospital__hospital_id=hospital
        )

    if status == "active":
        doctors = doctors.filter(a_status=True)

    elif status == "inactive":
        doctors = doctors.filter(a_status=False)

    context = {

        "doctors": doctors,

        "hospitals": Hospital.objects.order_by("name"),
        "total_doctors": Doctor.objects.count(),

        "active_doctors": Doctor.objects.filter(
            a_status=True
        ).count(),

        "inactive_doctors": Doctor.objects.filter(
            a_status=False
        ).count(),

        "hospital_count": Hospital.objects.count(),

        "search": search,
        "selected_hospital": hospital,
        "selected_status": status,

    }

    return render(
        request,
        "admin_dashboard/doctors.html",
        context
    )

@login_required
def add_doctor(request):

    if request.method == "POST":

        form = DoctorForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Doctor added successfully."
            )

            return redirect("admin_doctors")

    else:

        form = DoctorForm()

    return render(
        request,
        "admin_dashboard/doctor_form.html",
        {
            "form": form,
            "title": "Add Doctor",
            "button": "Add Doctor",
        },
    )


@login_required
def edit_doctor(request, doctor_id):

    doctor = get_object_or_404(
        Doctor,
        doctor_id=doctor_id
    )

    initial = {
        "username": doctor.user.username if doctor.user else "",
    }

    if request.method == "POST":

        form = DoctorForm(
            request.POST,
            instance=doctor,
            initial=initial,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Doctor updated successfully."
            )

            return redirect("admin_doctors")

    else:

        form = DoctorForm(
            instance=doctor,
            initial=initial,
        )

    return render(
        request,
        "admin_dashboard/doctor_form.html",
        {
            "form": form,
            "title": "Edit Doctor",
            "button": "Save Changes",
        },
    )

# delete doctor
@login_required
def delete_doctor(request, doctor_id):

    doctor = get_object_or_404(
        Doctor,
        doctor_id=doctor_id
    )

    appointment_exists = Appointment.objects.filter(
        doctor=doctor
    ).exists()

    if request.method == "POST":

        if appointment_exists:

            messages.error(
                request,
                "This doctor cannot be deleted because appointment records exist."
            )

            return redirect("admin_doctors")

        # Keep a reference to the user before deleting the doctor
        user = doctor.user

        doctor.delete()

        if user:
            user.delete()

        messages.success(
            request,
            "Doctor deleted successfully."
        )

        return redirect("admin_doctors")

    return render(
        request,
        "admin_dashboard/delete_doctor.html",
        {
            "doctor": doctor,
            "appointment_exists": appointment_exists,
        },
    )

# patients list page

@login_required
def admin_patients(request):

    patients = (
        Patients.objects
        .select_related("user")
        .annotate(
            appointment_count=Count("user__appointment")
        )
        .order_by("name")
    )

    search = request.GET.get("search", "")

    if search:

        patients = patients.filter(
            Q(name__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search) |
            Q(user__username__icontains=search)
        )

    context = {

        "patients": patients,

        "search": search,

        "total_patients": Patients.objects.count(),

        "appointment_count": Appointment.objects.count(),

        "active_patients": Patients.objects.count(),

        "doctor_count": Doctor.objects.count(),

    }

    return render(
        request,
        "admin_dashboard/patients.html",
        context
    )

# hospitals list page
@login_required
def admin_hospitals(request):

    hospitals = Hospital.objects.prefetch_related(
        "departments"
    ).order_by("name")

    search = request.GET.get("search", "")

    if search:
        hospitals = hospitals.filter(
            name__icontains=search
        )

    context = {

        "hospitals": hospitals,

        "search": search,

        "total_hospitals": Hospital.objects.count(),

        "total_departments": Department.objects.count(),

        "doctor_count": Doctor.objects.count(),

        "department_links": Department.objects.filter(
            hospitals__isnull=False
        ).distinct().count(),

    }

    return render(
        request,
        "admin_dashboard/hospitals.html",
        context
    )

@login_required
def add_hospital(request):

    if request.method == "POST":

        form = HospitalForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Hospital added successfully."
            )

            return redirect("admin_hospitals")

    else:

        form = HospitalForm()

    return render(
        request,
        "admin_dashboard/hospital_form.html",
        {
            "form": form,
            "title": "Add Hospital",
            "button": "Add Hospital",
        },
    )

@login_required
def edit_hospital(request, hospital_id):

    hospital = get_object_or_404(
        Hospital,
        hospital_id=hospital_id
    )

    if request.method == "POST":

        form = HospitalForm(
            request.POST,
            instance=hospital
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Hospital updated successfully."
            )

            return redirect("admin_hospitals")

    else:

        form = HospitalForm(instance=hospital)

    return render(
        request,
        "admin_dashboard/hospital_form.html",
        {
            "form": form,
            "title": "Edit Hospital",
            "button": "Save Changes",
        },
    )

@login_required
def delete_hospital(request, hospital_id):

    hospital = get_object_or_404(
        Hospital,
        hospital_id=hospital_id
    )

    doctor_exists = Doctor.objects.filter(
        hospital=hospital
    ).exists()

    if request.method == "POST":

        if doctor_exists:

            messages.error(
                request,
                "This hospital cannot be deleted because doctors are assigned to it."
            )

            return redirect("admin_hospitals")

        hospital.delete()

        messages.success(
            request,
            "Hospital deleted successfully."
        )

        return redirect("admin_hospitals")

    return render(
        request,
        "admin_dashboard/delete_hospital.html",
        {
            "hospital": hospital,
            "doctor_exists": doctor_exists,
        },
    )

# appointments list page
@login_required
@login_required
def admin_appointments(request):

    appointments = (
        Appointment.objects
        .select_related("patient", "doctor")
        .order_by("appointment_date", "appointment_time")
    )

    status = request.GET.get("status")
    date_filter = request.GET.get("filter")
    selected_date = request.GET.get("date")

    # Status filter
    if status:
        appointments = appointments.filter(status=status)

    # Today filter
    if date_filter == "today":
        today = timezone.now().date()
        appointments = appointments.filter(
            appointment_date=today
        )

    # Calendar date filter
    if selected_date:
        appointments = appointments.filter(
            appointment_date=selected_date
        )

    return render(
        request,
        "admin_dashboard/appointments.html",
        {
            "appointments": appointments,
            "selected_date": selected_date,
        }
    )

# doctor detail page
@login_required
def doctor_detail(request, doctor_id):

    doctor = get_object_or_404(Doctor, doctor_id=doctor_id)

    return render(request, "admin_dashboard/doctor_detail.html", {
        "doctor": doctor
    })


# toggle doctor status
@login_required
def toggle_doctor(request, doctor_id):

    doctor = get_object_or_404(Doctor, doctor_id=doctor_id)
    doctor.a_status = not doctor.a_status
    doctor.save()

    return redirect('admin_doctors')


# patient detail page
@login_required
@login_required
def patient_detail(request, user_id):

    user = get_object_or_404(
        User,
        id=user_id
    )

    patient = get_object_or_404(
        Patients,
        user=user
    )

    appointments = (
        Appointment.objects
        .filter(patient=user)
        .select_related(
            "doctor",
            "doctor__hospital",
            "doctor__department"
        )
        .order_by(
            "-appointment_date",
            "-appointment_time"
        )
    )

    total_appointments = appointments.count()

    completed_count = appointments.filter(
        status="completed"
    ).count()

    upcoming_count = appointments.filter(
        status="upcoming"
    ).count()

    cancelled_count = appointments.filter(
        status="cancelled"
    ).count()

    missed_count = appointments.filter(
        status="missed"
    ).count()

    total_spent = (
        Transaction.objects.filter(
            appointment__patient=user,
            payment_status="completed"
        ).aggregate(
            total=Sum("amount")
        )["total"] or 0
    )

    favorite_doctor = (
        Doctor.objects
        .filter(
            appointment__patient=user
        )
        .annotate(
            total=Count("appointment")
        )
        .order_by("-total")
        .first()
    )

    favorite_hospital = (
        Hospital.objects
        .filter(
            doctor__appointment__patient=user
        )
        .annotate(
            total=Count("doctor__appointment")
        )
        .order_by("-total")
        .first()
    )

    next_appointment = (
        appointments
        .filter(
            status="upcoming"
        )
        .first()
    )

    last_appointment = (
        appointments
        .exclude(
            status="upcoming"
        )
        .first()
    )

    context = {

        "patient": patient,

        "appointments": appointments,

        "total_appointments": total_appointments,

        "completed_count": completed_count,

        "upcoming_count": upcoming_count,

        "cancelled_count": cancelled_count,

        "missed_count": missed_count,

        "total_spent": total_spent,

        "favorite_doctor": favorite_doctor,

        "favorite_hospital": favorite_hospital,

        "next_appointment": next_appointment,

        "last_appointment": last_appointment,

    }

    return render(
        request,
        "admin_dashboard/patient_detail.html",
        context
    )

@login_required
def edit_patient(request, patient_id):

    patient = get_object_or_404(
        Patients,
        patient_id=patient_id
    )

    if request.method == "POST":

        form = PatientForm(
            request.POST,
            instance=patient
        )

        if form.is_valid():

            form.save()

            # Keep the linked User email in sync
            if patient.user:
                patient.user.email = patient.email
                patient.user.save()

            messages.success(
                request,
                "Patient updated successfully."
            )

            return redirect("admin_patients")

    else:

        form = PatientForm(instance=patient)

    return render(
        request,
        "admin_dashboard/patient_form.html",
        {
            "form": form,
            "title": "Edit Patient",
            "button": "Save Changes",
        },
    )


@login_required
def delete_patient(request, patient_id):

    patient = get_object_or_404(
        Patients,
        patient_id=patient_id
    )

    appointment_exists = Appointment.objects.filter(
        patient=patient.user
    ).exists()

    if request.method == "POST":

        if appointment_exists:

            messages.error(
                request,
                "This patient cannot be deleted because appointment records exist."
            )

            return redirect("admin_patients")

        user = patient.user

        patient.delete()

        if user:
            user.delete()

        messages.success(
            request,
            "Patient deleted successfully."
        )

        return redirect("admin_patients")

    return render(
        request,
        "admin_dashboard/delete_patient.html",
        {
            "patient": patient,
            "appointment_exists": appointment_exists,
        },
    )

# hospital detail page
@login_required
def hospital_detail(request, hospital_id):

    hospital = get_object_or_404(Hospital, hospital_id=hospital_id)
    departments = hospital.departments.all()

    return render(request, "admin_dashboard/hospital_detail.html", {
        "hospital": hospital,
        "departments": departments
    })

#doctor's leave request
@login_required
def admin_leave_requests(request):

    leaves = (
        DoctorLeave.objects
        .select_related("doctor", "doctor__hospital")
        .filter(is_deleted=False)
        .order_by("-start_date")
    )

    context = {
        "leaves": leaves,
    }

    return render(
        request,
        "admin_dashboard/leave_requests.html",
        context
    )

# calendar api for fullcalendar
@login_required
def calendar_events(request):

    appointments = (
        Appointment.objects
        .values("appointment_date")
        .annotate(total=Count("appointment_id"))
        .order_by("appointment_date")
    )

    events = []

    for appt in appointments:

        total = appt["total"]

        events.append({
            "title": f"🩺 {total} Appointment{'s' if total > 1 else ''}",
            "start": str(appt["appointment_date"]),
            "allDay": True,
        })

    return JsonResponse(events, safe=False)

@login_required
def admin_payments(request):

    transactions = (
        Transaction.objects
        .select_related(
            "appointment",
            "appointment__patient",
            "appointment__doctor"
        )
        .order_by("-created_at")
    )

    status = request.GET.get("status")
    today = request.GET.get("today")

    # Filter by payment status
    if status:
        transactions = transactions.filter(
            payment_status=status
        )

    # Show only today's completed payments
    if today == "1":
        transactions = transactions.filter(
            payment_status="completed",
            updated_at__date=timezone.now().date()
        )

    return render(
        request,
        "admin_dashboard/payments.html",
        {
            "transactions": transactions
        }
    )


@login_required
def payment_detail(request, transaction_id):

    transaction = get_object_or_404(
        Transaction.objects.select_related(
            "appointment",
            "appointment__patient",
            "appointment__doctor"
        ),
        id=transaction_id
    )

    return render(
        request,
        "admin_dashboard/payment_detail.html",
        {
            "transaction": transaction
        }
    )


@login_required
def mark_payment_paid(request, transaction_id):

    transaction = get_object_or_404(
        Transaction,
        id=transaction_id
    )

    if transaction.payment_method != "cash":

        messages.error(
            request,
            "Only cash payments can be updated."
        )

        return redirect(
            "payment_detail",
            transaction_id=transaction.id
        )

    transaction.payment_status = "completed"

    transaction.save()

    appointment = transaction.appointment

    create_notification(
        patient=appointment.patient,
        appointment=appointment,
        title="Payment Successful",
        message=(
            f"Your payment of "
            f"Rs. {transaction.amount} "
            f"has been received."
        ),
        notification_type="payment",
        reminder_type="general"
    )

    messages.success(
        request,
        "Cash payment marked as completed."
    )

    return redirect(
        "payment_detail",
        transaction_id=transaction.id
    )

@login_required
def mark_payment_unpaid(request, transaction_id):

    transaction = get_object_or_404(
        Transaction,
        id=transaction_id
    )

    if transaction.payment_method != "cash":

        messages.error(
            request,
            "Only cash payments can be updated."
        )

        return redirect(
            "payment_detail",
            transaction_id=transaction.id
        )

    transaction.payment_status = "pending"

    transaction.save()

    messages.success(
        request,
        "Payment changed back to Pending."
    )

    return redirect(
        "payment_detail",
        transaction_id=transaction.id
    )

#receipt

@login_required
def payment_receipt(request, transaction_id):

    transaction = get_object_or_404(
        Transaction.objects.select_related(
            "appointment",
            "appointment__doctor",
            "appointment__patient",
            "appointment__doctor__hospital",
        ),
        id=transaction_id
    )

    return render(
    request,
    "payments/receipt.html",
        {
            "transaction": transaction,
            "is_admin": True,
        }
    )


#appove or reject leave
@login_required
def approve_leave(request, leave_id):

    leave = get_object_or_404(
        DoctorLeave,
        id=leave_id
    )

    leave.status = "approved"
    leave.save()

    messages.success(
        request,
        "Leave approved successfully."
    )

    return redirect("admin_leave_requests")


@login_required
def reject_leave(request, leave_id):

    leave = get_object_or_404(
        DoctorLeave,
        id=leave_id
    )

    leave.status = "rejected"
    leave.save()

    messages.success(
        request,
        "Leave rejected successfully."
    )

    return redirect("admin_leave_requests")



@login_required
def admin_approve_appointment(request, appointment_id):

    appointment = get_object_or_404(
        Appointment,
        appointment_id=appointment_id
    )

    appointment.approval_status = "approved"
    appointment.review_reason = ""
    appointment.save()

    create_notification(
        patient=appointment.patient,
        appointment=appointment,
        title="Appointment Approved",
        message=(
            f"Your appointment with "
            f"{appointment.doctor.name} on "
            f"{appointment.appointment_date} at "
            f"{appointment.appointment_time} "
            f"has been approved."
        ),
        notification_type="appointment",
        reminder_type="general",
    )

    messages.success(
        request,
        "Appointment approved successfully."
    )

    return redirect("admin_appointments")


@login_required
def admin_reject_appointment(request, appointment_id):

    appointment = get_object_or_404(
        Appointment,
        appointment_id=appointment_id
    )

    appointment.approval_status = "rejected"
    appointment.save()

    create_notification(
        patient=appointment.patient,
        appointment=appointment,
        title="Appointment Rejected",
        message=(
            f"Your appointment with "
            f"{appointment.doctor.name} on "
            f"{appointment.appointment_date} at "
            f"{appointment.appointment_time} "
            f"has been rejected."
        ),
        notification_type="appointment",
        reminder_type="general",
    )

    messages.success(
        request,
        "Appointment rejected successfully."
    )

    return redirect("admin_appointments")