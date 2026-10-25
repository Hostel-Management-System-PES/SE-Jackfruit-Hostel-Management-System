"""Registration and login forms (REQ-1, REQ-21)."""
import re

from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import AuthenticationForm

from .models import User

SRN_PATTERN = re.compile(r"^[A-Za-z0-9]{6,20}$")
PHONE_PATTERN = re.compile(r"^\+?\d{10,15}$")


class RegistrationForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField(max_length=100)
    srn = forms.CharField(label="SRN", max_length=20)
    guardian_contact = forms.CharField(label="Guardian contact number", max_length=15)
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput, strip=False)
    password2 = forms.CharField(label="Confirm password", widget=forms.PasswordInput, strip=False)

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if not name:
            raise forms.ValidationError("Name is required.")
        return name

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email is already registered.")
        return email

    def clean_srn(self):
        srn = self.cleaned_data["srn"].strip().upper()
        if not SRN_PATTERN.match(srn):
            raise forms.ValidationError("SRN must be 6 to 20 letters or digits.")
        if User.objects.filter(srn__iexact=srn).exists():
            raise forms.ValidationError("An account with this SRN is already registered.")
        return srn

    def clean_guardian_contact(self):
        contact = self.cleaned_data["guardian_contact"].strip().replace(" ", "")
        if not PHONE_PATTERN.match(contact):
            raise forms.ValidationError("Enter a valid phone number (10 to 15 digits).")
        return contact

    def clean(self):
        cleaned = super().clean()
        password1 = cleaned.get("password1")
        password2 = cleaned.get("password2")
        if password1 and password2 and password1 != password2:
            self.add_error("password2", "The two passwords do not match.")
        elif password1:
            candidate = User(
                name=cleaned.get("name", ""),
                email=cleaned.get("email", ""),
            )
            try:
                password_validation.validate_password(password1, candidate)
            except forms.ValidationError as error:
                self.add_error("password1", error)
        return cleaned


class LoginForm(AuthenticationForm):
    """REQ-21: email or SRN + password; accounts that are not Verified are refused."""

    username = forms.CharField(label="Email or SRN", max_length=100)

    error_messages = {
        "invalid_login": "Invalid credentials. Check your email/SRN and password.",
        "inactive": "This account is inactive.",
        "pending": "Your account is pending admin approval.",
        "rejected": "Your registration was rejected. Contact the hostel office.",
    }

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if user.registration_status == User.Status.PENDING:
            raise forms.ValidationError(self.error_messages["pending"], code="pending")
        if user.registration_status == User.Status.REJECTED:
            raise forms.ValidationError(self.error_messages["rejected"], code="rejected")
