from django.contrib import admin
from .models import Doctor, DoctorAvailability, DoctorLeave
from hospitals.models import Department


class DoctorAdmin(admin.ModelAdmin):
    list_display = ("name", "hospital", "department", "specialization")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "department":
            kwargs["queryset"] = Department.objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(DoctorAvailability)
class DoctorAvailabilityAdmin(admin.ModelAdmin):
    list_display = (
        "doctor",
        "day_of_week",
        "start_time",
        "end_time",
    )


@admin.register(DoctorLeave)
class DoctorLeaveAdmin(admin.ModelAdmin):
    list_display = (
        "doctor",
        "start_date",
        "end_date",
        "is_deleted",
    )


admin.site.register(Doctor, DoctorAdmin)