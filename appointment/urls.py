from django.urls import path
from . import views

urlpatterns = [
    path("book/<int:doctor_id>/", views.book_appointment, name="book_appointment"),
    path("confirm/", views.confirm_appointment, name="confirm_appointment"),
    path("upcoming/", views.upcoming_appointments, name="upcoming_appointments"),

    path("doctor/complete/<int:appointment_id>/", views.doctor_mark_completed, name="doctor_mark_completed"),
    path("doctor/missed/<int:appointment_id>/", views.doctor_mark_missed, name="doctor_mark_missed"),
    path("doctor/reschedule/<int:appointment_id>/", views.doctor_reschedule, name="doctor_reschedule"),
    path(
    "cancel/<int:appointment_id>/",
    views.cancel_appointment,
    name="cancel_appointment"
),
path(
    "report/<int:appointment_id>/",
    views.upload_report,
    name="upload_report",
),
path(
    "reports/",
    views.patient_reports,
    name="patient_reports",
),




path(
    "report/<int:appointment_id>/view/",
    views.view_report,
    name="view_report",
),

path(
    "report/<int:appointment_id>/edit/",
    views.edit_report,
    name="edit_report",
),

]