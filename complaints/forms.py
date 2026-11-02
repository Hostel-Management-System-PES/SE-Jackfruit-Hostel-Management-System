"""Forms for complaints and leave requests (REQ-17, REQ-19)."""
from django import forms

from .services import MAX_DESCRIPTION, MAX_REASON


class ComplaintForm(forms.Form):
    description = forms.CharField(
        max_length=MAX_DESCRIPTION,
        widget=forms.Textarea(attrs={"rows": 4}),
        error_messages={"required": "Description is required."},
    )


class LeaveForm(forms.Form):
    start_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    reason = forms.CharField(
        max_length=MAX_REASON,
        widget=forms.Textarea(attrs={"rows": 2}),
        error_messages={"required": "Reason is required."},
    )

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get("start_date")
        end = cleaned.get("end_date")
        if start and end and end < start:
            self.add_error("end_date", "End date cannot be before start date.")
        return cleaned
