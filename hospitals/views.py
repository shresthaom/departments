from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Hospital, Department
from doctors.models import Doctor


# -------------------------------
# 🏥 Hospital List
# -------------------------------
def hospital_list(request):
    query = request.GET.get('q')

    hospitals = Hospital.objects.all()
    if query:
        hospitals = hospitals.filter(name__icontains=query)

    return render(request, 'hospitals/hospital_list.html', {
        'hospitals': hospitals,
        'query': query
    })


# -------------------------------
# 🏥 Hospital Detail
# -------------------------------
def hospital_detail(request, hospital_id):
    hospital = get_object_or_404(Hospital, hospital_id=hospital_id)

    # only available doctors in this hospital
    doctors = Doctor.objects.filter(hospital=hospital, a_status=True)

    search = request.GET.get('search', '')
    dept_id = request.GET.get('department', '')

    # 🔍 Search doctors by name or specialization
    if search:
        doctors = doctors.filter(
            Q(name__icontains=search) |
            Q(specialization__icontains=search)
        )

    # 🎯 Filter by department
    if dept_id:
        doctors = doctors.filter(department_id=dept_id)

    # 🏥 Departments offered by this hospital (ManyToMany)
    departments = Department.objects.filter(hospitals=hospital)

    return render(request, 'hospitals/hospital_detail.html', {
        'hospital': hospital,
        'doctors': doctors.distinct(),
        'departments': departments,
        'search': search,
        'dept_id': dept_id
    })


# -------------------------------
# 🧪 Department Detail
# -------------------------------
def department_detail(request, department_id):
    department = get_object_or_404(Department, id=department_id)

    # safer query (works even without related_name)
    doctors = Doctor.objects.filter(department=department, a_status=True)

    return render(request, 'hospitals/department_detail.html', {
        'department': department,
        'doctors': doctors
    })