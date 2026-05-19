from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from doctors.models import Doctor
from hospitals.models import Hospital, Department

# search doctor

class SearchDoctorTest(TestCase):

    def setUp(self):

        self.hospital = Hospital.objects.create(
            name="City Hospital",
            address="Kathmandu",
            phone="123456",
            email="hospital@test.com"
        )

        self.department = Department.objects.create(
            name="Cardiology"
        )

        self.department.hospitals.add(self.hospital)

        self.user = User.objects.create_user(
            username="doctor1",
            password="pass123"
        )

        self.doctor = Doctor.objects.create(
            user=self.user,
            name="Dr Sharma",
            qualification="MBBS",
            specialization="Cardiology",
            experience_years=5,
            hospital=self.hospital,
            department=self.department,
            email="doctor@test.com",
            fees=1000,
            phone="9800000000",
            a_status=True
        )

    def test_doctor_list_displays_correct_doctor(self):

        response = self.client.get(
            reverse('doctor_list')
        )

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "Dr Sharma")

    def test_available_filter(self):

        response = self.client.get(
            reverse('doctor_list') + "?available=true"
        )

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "Dr Sharma")

    
# book appointment
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from doctors.models import Doctor
from hospitals.models import Hospital, Department
from appointment.models import Appointment


class BookAppointmentTest(TestCase):

    def setUp(self):

        self.patient = User.objects.create_user(
            username="patient1",
            password="pass123"
        )

        self.hospital = Hospital.objects.create(
            name="City Hospital",
            address="Kathmandu",
            phone="123456",
            email="hospital@test.com"
        )

        self.department = Department.objects.create(
            name="Cardiology"
        )

        self.department.hospitals.add(self.hospital)

        self.doctor_user = User.objects.create_user(
            username="doctor1",
            password="pass123"
        )

        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            name="Dr Sharma",
            qualification="MBBS",
            specialization="Cardiology",
            experience_years=5,
            hospital=self.hospital,
            department=self.department,
            email="doctor@test.com",
            fees=1000,
            phone="9800000000",
            a_status=True
        )

    def test_book_appointment_successfully(self):

        self.client.login(
            username="patient1",
            password="pass123"
        )

        session = self.client.session

        session["appointment_data"] = {
            "doctor_id": self.doctor.doctor_id,
            "appointment_date": "2026-06-01",
            "appointment_time": "10:00"
        }

        session.save()

        response = self.client.post(
            reverse('confirm_appointment')
        )

        self.assertEqual(response.status_code, 302)

        self.assertTrue(
            Appointment.objects.filter(
                doctor=self.doctor,
                patient=self.patient
            ).exists()
        )

    
from doctors.models import DoctorAvailability


class SetAvailabilityTest(TestCase):

    def setUp(self):

        self.hospital = Hospital.objects.create(
            name="Hospital",
            address="KTM",
            phone="123",
            email="hospital4@test.com"
        )

        self.department = Department.objects.create(
            name="Neuro"
        )

        self.department.hospitals.add(self.hospital)

        self.user = User.objects.create_user(
            username="doctor1",
            password="pass123"
        )

        self.doctor = Doctor.objects.create(
            user=self.user,
            name="Doctor",
            qualification="MBBS",
            specialization="Neuro",
            experience_years=3,
            hospital=self.hospital,
            department=self.department,
            email="doctor4@test.com",
            fees=1000,
            phone="9800000000"
        )

    def test_set_availability(self):

        self.client.login(
            username="doctor1",
            password="pass123"
        )

        response = self.client.post(
            reverse('set_availability'),
            {
                "day_of_week": 1,
                "start_time": "09:00",
                "end_time": "17:00"
            }
        )

        self.assertEqual(response.status_code, 302)

        self.assertTrue(
            DoctorAvailability.objects.filter(
                doctor=self.doctor,
                day_of_week=1
            ).exists()
        )