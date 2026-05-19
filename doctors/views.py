from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count

from .models import Doctor, DoctorAvailability, DoctorLeave
from .forms import DoctorLeaveForm
from appointment.models import Appointment

def calculate_score_with_breakdown(doctor):

    score = 0
    breakdown = []

    # availability
    if doctor.a_status:
        score += 40
        breakdown.append(("Availability", 40))

    # experience
    exp_score = doctor.experience_years * 2
    score += exp_score
    breakdown.append(("Experience", exp_score))

    # qualification
    qualification_scores = {
        "MBBS": 10,
        "MD": 20,
        "MS": 20,
        "BDS": 10,
        "MDS": 18,
        "DM": 25,
        "MCh": 25,
        "FCPS": 22,
        "PhD": 15,
    }

    for q, points in qualification_scores.items():
        if q in doctor.qualification:
            score += points
            breakdown.append(("Qualification", points, q))
            break

    return score, breakdown


# doctor list
def doctor_list(request):

    hospital_id = request.GET.get("hospital")
    department_id = request.GET.get("department")
    available = request.GET.get("available")

    doctors = Doctor.objects.all()

    if hospital_id:
        doctors = doctors.filter(hospital_id=hospital_id)

    if department_id:
        doctors = doctors.filter(department_id=department_id)

    if available == "true":
        doctors = doctors.filter(a_status=True)

    ranked = []

    for doctor in doctors:
        score, breakdown = calculate_score_with_breakdown(doctor)

        ranked.append({
            "doctor": doctor,
            "score": score,
            "breakdown": breakdown
        })

    ranked.sort(key=lambda x: x["score"], reverse=True)

    # assign rank number
    for i, item in enumerate(ranked, start=1):
        item["rank"] = i

    return render(request, "doctors/doctors.html", {
        "ranked_doctors": ranked
    })

# doctor detail
def doctor_detail(request, doctor_id):
    doctor = get_object_or_404(Doctor, doctor_id=doctor_id)

    return render(request, "doctors/doctor_detail.html", {
        "doctor": doctor
    })


# doctor dashboard
@login_required
def doctor_dashboard(request):

    if not hasattr(request.user, 'doctor'):
        return redirect('home')

    doctor = request.user.doctor
    today = timezone.now().date()

    today_appts = Appointment.objects.filter(doctor=doctor, appointment_date=today)
    upcoming_appts = Appointment.objects.filter(doctor=doctor, appointment_date__gt=today)

    leaves = DoctorLeave.objects.filter(doctor=doctor, is_deleted=False)
    availability = DoctorAvailability.objects.filter(doctor=doctor)

    appointment_stats = Appointment.objects.filter(
        doctor=doctor
    ).values('status').annotate(total=Count('status'))

    leave_count = leaves.count()

    today_availability = DoctorAvailability.objects.filter(
        doctor=doctor,
        day_of_week=today.weekday()
    ).first()

    return render(request, "doctors/dashboard.html", {
        "doctor": doctor,
        "today_count": today_appts.count(),
        "upcoming_count": upcoming_appts.count(),
        "leaves": leaves,
        "availability": availability,
        "today_availability": today_availability,
        "appointment_stats": appointment_stats,
        "leave_count": leave_count,
        "today": today,
        "weekday": today.weekday()
    })


# add leave
@login_required
def add_leave(request):

    doctor = request.user.doctor

    if request.method == "POST":
        form = DoctorLeaveForm(request.POST)

        if form.is_valid():
            leave = form.save(commit=False)
            leave.doctor = doctor

            overlap = DoctorLeave.objects.filter(
                doctor=doctor,
                is_deleted=False,
                start_date__lte=leave.end_date,
                end_date__gte=leave.start_date
            ).exists()

            if overlap:
                return render(request, "doctors/add_leave.html", {
                    "error": "leave overlaps with existing leave",
                    "form": form
                })

            leave.save()
            return redirect("doctor_dashboard")

    else:
        form = DoctorLeaveForm()

    return render(request, "doctors/add_leave.html", {
        "form": form
    })


# edit leave
@login_required
def edit_leave(request, leave_id):

    doctor = request.user.doctor
    leave = get_object_or_404(DoctorLeave, id=leave_id, doctor=doctor)

    if request.method == "POST":
        form = DoctorLeaveForm(request.POST, instance=leave)

        if form.is_valid():
            form.save()
            return redirect("doctor_dashboard")

    else:
        form = DoctorLeaveForm(instance=leave)

    return render(request, "doctors/edit_leave.html", {
        "form": form
    })


# delete leave (soft delete safe fix)
@login_required
@login_required
def delete_leave(request, leave_id):

    doctor = request.user.doctor

    leave = get_object_or_404(
        DoctorLeave,
        id=leave_id,
        doctor=doctor,
        is_deleted=False
    )

    # show confirmation page first
    if request.method == "POST":

        leave.is_deleted = True
        leave.save(update_fields=['is_deleted'])

        return redirect("doctor_dashboard")

    return render(request, "doctors/confirm_delete_leave.html", {
        "leave": leave
    })
# set availability
@login_required
def set_availability(request):

    doctor = request.user.doctor

    if request.method == "POST":

        day = request.POST.get("day_of_week")
        start = request.POST.get("start_time")
        end = request.POST.get("end_time")

        DoctorAvailability.objects.create(
            doctor=doctor,
            day_of_week=day,
            start_time=start,
            end_time=end
        )

        return redirect("doctor_dashboard")

    return render(request, "doctors/set_availability.html")