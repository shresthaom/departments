from django.shortcuts import render,redirect
from .models import Patients
from django.contrib.auth.models import User
from django .contrib.auth import login,logout,authenticate

# Create your views here.


#patient register page

def register(request):
    if request.method=="POST":
        username=request.POST['username']
        password=request.POST['password']

        user=User.objects.create_user(username=username,password=password)
        user.save()

        return redirect('login')
    
    return render(request,'patients/register.html')

#patient login page

def user_login(request):
    if request.method=="POST":
        username=request.POST['username']
        password=request.POST['password']

        user=authenticate(request,username=username,password=password)

        if user is not None:
            login(request,user)
            return redirect('patient_dashboard')
        
    return render(request,'patients/login.html')


#patient logout

def user_logout(request):
    logout(request)
    return redirect('login')


#patient dashboard

def patient_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    return render(request,'patients/patient_dashboard.html')





#registering patient details after login
def success(request):
    return render(request, 'patients/success.html')

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

        return redirect('success')
    
    return render(request,'patients/patients_form.html')

