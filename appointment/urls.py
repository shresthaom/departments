from django.urls import path
from . import views

urlpatterns = [
    path("book/<int:doctor_id>/", views.book_appointment, name="book_appointment"),
    path("confirm/", views.confirm_appointment, name="confirm_appointment"),
    path("upcoming/", views.upcoming_appointments, name="upcoming_appointments"),
    path("complete/<int:appointment_id>/", views.mark_completed, name="mark_completed"),
    path('appointment/reschedule/<int:appointment_id>/', views.reschedule_appointment, name='reschedule_appointment')
]
