"""Views of the Complaints & Leave module (REQ-17, REQ-19)."""
from django.contrib import messages
from django.shortcuts import redirect, render

from accounts.decorators import admin_required, student_required
from rooms.services import get_student_room

from . import services
from .forms import ComplaintForm, LeaveForm


@student_required
def student_page(request):
    """Complaints & Leave page: complaint form and list, leave form and list."""
    action = request.POST.get("action") if request.method == "POST" else None
    complaint_form = ComplaintForm(request.POST if action == "complaint" else None)
    leave_form = LeaveForm(request.POST if action == "leave" else None)
    room = get_student_room(request.user)

    if action == "complaint" and complaint_form.is_valid():
        try:
            services.file_complaint(
                student=request.user, description=complaint_form.cleaned_data["description"]
            )
        except services.RequestError as error:
            messages.error(request, str(error))
            if error.field:
                complaint_form.add_error(error.field, str(error))
        else:
            messages.success(request, "Your complaint was submitted and is Open.")
            return redirect("complaints:student_page")

    if action == "leave" and leave_form.is_valid():
        data = leave_form.cleaned_data
        try:
            services.submit_leave(
                student=request.user,
                start_date=data["start_date"],
                end_date=data["end_date"],
                reason=data["reason"],
            )
        except services.RequestError as error:
            messages.error(request, str(error))
            if error.field:
                leave_form.add_error(error.field, str(error))
        else:
            messages.success(request, "Your leave request was submitted and is Pending.")
            return redirect("complaints:student_page")

    context = {
        "room": room,
        "complaint_form": complaint_form,
        "leave_form": leave_form,
        "complaints": services.student_complaints(request.user),
        "leaves": services.student_leaves(request.user),
    }
    return render(request, "complaints/student_page.html", context)


@admin_required
def admin_page(request):
    """Complaints & Leave Requests page for the admin (view only in Sprint 1)."""
    context = {"complaints": services.all_complaints(), "leaves": services.all_leaves()}
    return render(request, "complaints/admin_page.html", context)
