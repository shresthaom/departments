from django.contrib import admin
from .models import Doctor
from hospitals.models import Department

class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'hospital', 'department', 'specialization')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "department":
            kwargs["queryset"] = Department.objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(Doctor, DoctorAdmin)