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

class ViewAppointmentStatusTest(TestCase):

    def setUp(self):

        self.patient = User.objects.create_user(
            username="patient1",
            password="pass123"
        )

        self.hospital = Hospital.objects.create(
            name="Hospital",
            address="KTM",
            phone="123",
            email="hospital3@test.com"
        )

        self.department = Department.objects.create(
            name="Dental"
        )

        self.department.hospitals.add(self.hospital)

        self.doctor_user = User.objects.create_user(
            username="doctor1",
            password="pass123"
        )

        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            name="Doctor",
            qualification="MBBS",
            specialization="Dental",
            experience_years=2,
            hospital=self.hospital,
            department=self.department,
            email="doctor3@test.com",
            fees=1000,
            phone="9800000000"
        )

        self.appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date="2026-06-01",
            appointment_time="10:00",
            status="Completed"
        )

    def test_correct_status_displayed(self):

        self.client.login(
            username="patient1",
            password="pass123"
        )

        response = self.client.get(
            reverse('upcoming_appointments')
        )

        self.assertContains(
            response,
            "Completed"
        )

# cancel appointment
class AppointmentCancellationTest(TestCase):

    def setUp(self):

        # patient
        self.patient = User.objects.create_user(
            username="patient1",
            password="pass123"
        )

        # hospital
        self.hospital = Hospital.objects.create(
            name="Test Hospital",
            address="Kathmandu",
            phone="123456",
            email="hospital2@test.com"
        )

        # department
        self.department = Department.objects.create(
            name="ENT"
        )

        self.department.hospitals.add(self.hospital)

        # doctor user
        self.doctor_user = User.objects.create_user(
            username="doctor1",
            password="pass123"
        )

        # doctor
        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            name="Doctor",
            qualification="MBBS",
            specialization="ENT",
            experience_years=3,
            hospital=self.hospital,
            department=self.department,
            email="doctor2@test.com",
            fees=1000,
            phone="9800000000"
        )

        # appointment
        self.appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date="2026-06-01",
            appointment_time="10:00",
            status="upcoming"
        )

    def test_appointment_status_updated_after_cancellation(self):

        # login patient
        self.client.login(
            username="patient1",
            password="pass123"
        )

        # cancel appointment
        response = self.client.get(
            reverse(
                'cancel_appointment',
                args=[self.appointment.appointment_id]
            )
        )

        # refresh from db
        self.appointment.refresh_from_db()

        # check redirect
        self.assertEqual(response.status_code, 302)

        # check status updated
        self.assertEqual(
            self.appointment.status,
            "cancelled"
        )