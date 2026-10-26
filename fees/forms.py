"""Forms for setting fees and recording payments (REQ-11, REQ-12, REQ-14)."""
from decimal import Decimal

from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone

MAX_AMOUNT = Decimal("99999999.99")


class StudentChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.srn} - {obj.name}"


def student_queryset():
    user_model = get_user_model()
    return user_model.objects.filter(role=user_model.Role.STUDENT).order_by("srn")


class PaymentForm(forms.Form):
    student = StudentChoiceField(queryset=None)
    amount = forms.DecimalField(
        label="Amount (₹)", max_digits=10, decimal_places=2, max_value=MAX_AMOUNT
    )
    payment_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only students who have a fee can receive a payment.
        self.fields["student"].queryset = student_queryset().filter(fee__isnull=False)
        self.fields["payment_date"].initial = timezone.localdate()

    def clean_amount(self):
        amount = self.cleaned_data["amount"]
        if amount <= 0:
            raise forms.ValidationError("Payment amount must be greater than 0.")
        return amount


class FeeForm(forms.Form):
    student = StudentChoiceField(queryset=None)
    amount = forms.DecimalField(
        label="Fee amount (₹)", max_digits=10, decimal_places=2, max_value=MAX_AMOUNT
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["student"].queryset = student_queryset()

    def clean_amount(self):
        amount = self.cleaned_data["amount"]
        if amount <= 0:
            raise forms.ValidationError("Fee amount must be greater than 0.")
        return amount
