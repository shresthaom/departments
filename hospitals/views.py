from django.shortcuts import render, get_object_or_404
from .models import Hospital, Department
from doctors.models import Doctor


# Hospital List
def hospital_list(request):
    query = request.GET.get('q')

    hospitals = Hospital.objects.all()
    if query:
        hospitals = hospitals.filter(name__icontains=query)

    return render(request, 'hospitals/hospital_list.html', {
        'hospitals': hospitals,
        'query': query
    })


# Hospital detail



def hospital_detail(request, hospital_id):
    hospital = get_object_or_404(Hospital, hospital_id=hospital_id)

    doctors = Doctor.objects.filter(hospital=hospital, a_status=True)

    search = request.GET.get('search', '')
    dept_id = request.GET.get('department', '')

    # Search doc by name or dept
    if search:
        doctors = doctors.filter(
            name__icontains=search
        ) | doctors.filter(
            specialization__icontains=search
        )

    # Filter by dept
    if dept_id:
        doctors = doctors.filter(department__department_id=dept_id)

    # only departments of this hospital
    departments = Department.objects.filter(hospital=hospital)

    return render(request, 'hospitals/hospital_detail.html', {
        'hospital': hospital,
        'doctors': doctors.distinct(),
        'departments': departments,
        'search': search,
        'dept_id': dept_id
    })

# Department detail 
def department_detail(request, department_id):
    department = get_object_or_404(Department, department_id=department_id)
    doctors = department.doctors.filter(a_status=True)

    return render(request, 'hospitals/department_detail.html', {
        'department': department,
        'doctors': doctors
    })