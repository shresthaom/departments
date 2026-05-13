from django import forms
from datetime import date
from .models import DoctorLeave

# leave form with validation
class DoctorLeaveForm(forms.ModelForm):

    class Meta:
        model = DoctorLeave
        fields = ['start_date', 'end_date', 'reason']

    def clean(self):
        cleaned_data = super().clean()

        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        # validate date range
        if start_date and end_date:
            if end_date < start_date:
                raise forms.ValidationError("end date cannot be before start date")

            if start_date < date.today():
                raise forms.ValidationError("start date cannot be in the past")

        return cleaned_data