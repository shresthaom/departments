from django.shortcuts import render,redirect
from .models import Patients

# Create your views here.

def register_patients(request):
    if request.method=="POST":
        name=request.POST.get('name')
        address=request.POST.get('address')
        phone=request.POST.get('phone')
        dob=request.POST.get('dob')
        gender=request.POST.get('gender')

        Patients.objects.create(

            name=name,
            address=address,
            phone=phone,
            dob=dob,
            gender=gender
        )

        return redirect('homepage')
    
    return render(request,'patients/patients_form.html')

