from django.contrib import admin
from .models import Hospital, Department

@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone', 'email')


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'hospital')
    list_filter = ('hospital',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('hospital')