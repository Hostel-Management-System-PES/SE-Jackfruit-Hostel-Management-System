"""Views of the Accounts module (REQ-1, REQ-2, REQ-3, REQ-4, REQ-5, REQ-21)."""
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST, require_safe

from hms.dashboard import collect_cards

from . import services
from .decorators import admin_required, student_required
from .forms import LoginForm, ProfileForm, RegistrationForm
from .models import User


@require_safe
def home(request):
    """Send each user to the dashboard for their role."""
    user = request.user
    if not user.is_authenticated:
        return redirect("accounts:login")
    if user.is_admin_role:
        return redirect("accounts:admin_dashboard")
    return redirect("accounts:student_dashboard")


def register(request):
    if request.user.is_authenticated:
        return redirect("accounts:home")
    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data
        services.register_student(
            name=data["name"],
            email=data["email"],
            srn=data["srn"],
            guardian_contact=data["guardian_contact"],
            password=data["password1"],
        )
        messages.success(
            request, "Registration submitted. Your account is pending admin approval."
        )
        return redirect("accounts:login")
    return render(request, "accounts/register.html", {"form": form})


class HMSLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True


@student_required
def student_dashboard(request):
    return render(
        request, "accounts/student_dashboard.html", {"cards": collect_cards(request.user)}
    )


@student_required
def profile(request):
    """REQ-5: My Profile. Always the logged-in student, so nobody can edit another profile."""
    user = request.user
    form = ProfileForm(
        request.POST or None,
        initial={"name": user.name, "guardian_contact": user.guardian_contact},
    )
    if request.method == "POST" and form.is_valid():
        services.update_profile(
            user=user,
            name=form.cleaned_data["name"],
            guardian_contact=form.cleaned_data["guardian_contact"],
        )
        messages.success(request, "Your profile was updated.")
        return redirect("accounts:profile")
    return render(request, "accounts/profile.html", {"form": form})


@admin_required
def admin_dashboard(request):
    context = {
        "cards": collect_cards(request.user),
        "pending": services.pending_students(),
    }
    return render(request, "accounts/admin_dashboard.html", context)


@admin_required
@require_POST
def decide_registration(request, user_id):
    decision = request.POST.get("decision")
    try:
        user = services.decide_registration(user_id=user_id, decision=decision)
    except services.AccountError as error:
        messages.error(request, str(error))
    else:
        if user.registration_status == User.Status.VERIFIED:
            messages.success(request, f"{user.name} has been approved.")
        else:
            messages.success(request, f"{user.name} has been rejected.")
    return redirect("accounts:admin_dashboard")
