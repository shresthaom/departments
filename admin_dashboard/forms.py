from django import forms
from django.contrib.auth.models import User

from patients.models import Patients
from django import forms

from doctors.models import Doctor
from hospitals.models import Hospital, Department


class DoctorForm(forms.ModelForm):

    username = forms.CharField(max_length=150)
    password = forms.CharField(
        widget=forms.PasswordInput(),
        required=False
    )

    class Meta:
        model = Doctor

        fields = [
            "name",
            "qualification",
            "specialization",
            "experience_years",
            "hospital",
            "department",
            "email",
            "phone",
            "fees",
            "a_status",
        ]

        widgets = {

            "name": forms.TextInput(attrs={"class": "form-control"}),

            "qualification": forms.TextInput(attrs={"class": "form-control"}),

            "specialization": forms.TextInput(attrs={"class": "form-control"}),

            "experience_years": forms.NumberInput(attrs={"class": "form-control"}),

            "hospital": forms.Select(attrs={"class": "form-control"}),

            "department": forms.Select(attrs={"class": "form-control"}),

            "email": forms.EmailInput(attrs={"class": "form-control"}),

            "phone": forms.TextInput(attrs={"class": "form-control"}),

            "fees": forms.NumberInput(attrs={"class": "form-control"}),

            "a_status": forms.CheckboxInput(),
        }

    def save(self, commit=True):

        doctor = super().save(commit=False)

        if doctor.user is None:

            username = self.cleaned_data["username"]

            password = self.cleaned_data["password"]

            user = User.objects.create_user(
                username=username,
                password=password
            )

            doctor.user = user

        else:

            doctor.user.username = self.cleaned_data["username"]
            doctor.user.save()

            password = self.cleaned_data["password"]

            if password:
                doctor.user.set_password(password)
                doctor.user.save()

        if commit:
            doctor.save()

        return doctor




# Hospital form

class HospitalForm(forms.ModelForm):

    class Meta:

        model = Hospital

        fields = [
            "name",
            "address",
            "phone",
            "email",
        ]

        widgets = {

            "name": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "address": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "phone": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "email": forms.EmailInput(
                attrs={"class": "form-control"}
            ),

        }

# patient form

class PatientForm(forms.ModelForm):

    class Meta:

        model = Patients

        fields = [
            "name",
            "email",
            "phone",
            "address",
            "dob",
            "gender",
        ]

        widgets = {

            "dob": forms.DateInput(
                attrs={"type": "date"}
            ),

        }

    def clean_phone(self):

        phone = self.cleaned_data["phone"]

        qs = Patients.objects.filter(phone=phone)

        if self.instance.pk:

            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():

            raise forms.ValidationError(
                "Phone number already exists."
            )

        return phone

    def clean_email(self):

        email = self.cleaned_data["email"]

        qs = Patients.objects.filter(email=email)

        if self.instance.pk:

            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():

            raise forms.ValidationError(
                "Email already exists."
            )

        return email