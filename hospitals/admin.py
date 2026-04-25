from django.contrib import admin
from .models import Hospital, Department

@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone', 'email')


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_hospitals')
    list_filter = ('hospitals',)

    def get_hospitals(self, obj):
        return ", ".join([h.name for h in obj.hospitals.all()])
    
    get_hospitals.short_description = 'Hospitals'