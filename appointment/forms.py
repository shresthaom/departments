from django import forms
from .models import MedicalReport


class MedicalReportForm(forms.ModelForm):

    class Meta:
        model = MedicalReport
        fields = [
            "diagnosis",
            "prescription",
            "remarks",
            "report_file",
        ]

        widgets = {
            "diagnosis": forms.Textarea(attrs={"rows": 4}),
            "prescription": forms.Textarea(attrs={"rows": 4}),
            "remarks": forms.Textarea(attrs={"rows": 3}),
        }