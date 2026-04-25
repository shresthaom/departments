from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.utils import timezone

from .models import Hospital, Department
from doctors.models import Doctor
from appointment.models import Appointment
from appointment.views import get_appt_datetime


# -------------------------------
# 🏥 Hospital List
# -------------------------------
def hospital_list(request):
    query = request.GET.get('q', '')

    hospitals = Hospital.objects.all()
    if query:
        hospitals = hospitals.filter(name__icontains=query)

    return render(request, 'hospitals/hospital_list.html', {
        'hospitals': hospitals,
        'query': query
    })


# -------------------------------
# 🏥 Hospital Detail (FINAL)
# -------------------------------
def hospital_detail(request, hospital_id):
    hospital = get_object_or_404(Hospital, hospital_id=hospital_id)

    # 🧑‍⚕️ Doctors of this hospital
    doctors = Doctor.objects.filter(hospital=hospital, a_status=True)

    # 🔍 Search
    search = request.GET.get('search', '')
    if search:
        doctors = doctors.filter(
            Q(name__icontains=search) |
            Q(specialization__icontains=search)
        )

    # 🎯 Department filter
    dept_id = request.GET.get('department', '')
    if dept_id:
        doctors = doctors.filter(department__id=dept_id)

    # 🧠 -------- RANKING --------
    doctors = list(doctors.distinct())

    def calculate_score(doc):
        score = 0

        experience = getattr(doc, 'experience_years', 0) or 0
        qualification = getattr(doc, 'qualification', '') or ''

        score += experience * 5

        if "MD" in qualification:
            score += 30
        elif "MBBS" in qualification:
            score += 15

        if doc.a_status:
            score += 10

        return score

    for doc in doctors:
        doc.score = calculate_score(doc)

    doctors = sorted(doctors, key=lambda x: x.score, reverse=True)
    # --------------------------

    # 📚 Departments of this hospital
    departments = Department.objects.filter(hospitals=hospital)

    # 📅 Appointment summary (NEW)
    if request.user.is_authenticated:
        appointments = Appointment.objects.filter(patient=request.user)

        past = []
        upcoming = []
        now = timezone.now()

        for appt in appointments:
            if appt.status == "cancelled":
                continue

            if get_appt_datetime(appt) < now:
                past.append(appt)
            else:
                upcoming.append(appt)
    else:
        past = []
        upcoming = []

    # 📦 Final response
    return render(request, 'hospitals/hospital_detail.html', {
        'hospital': hospital,
        'doctors': doctors,
        'departments': departments,
        'search': search,
        'dept_id': dept_id,

        # appointment box
        'upcoming_count': len(upcoming),
        'past_count': len(past),
    })


# -------------------------------
# 🧪 Department Detail
# -------------------------------
def department_detail(request, department_id):
    department = get_object_or_404(Department, id=department_id)

    doctors = Doctor.objects.filter(department=department, a_status=True)

    return render(request, 'hospitals/department_detail.html', {
        'department': department,
        'doctors': doctors
    })
