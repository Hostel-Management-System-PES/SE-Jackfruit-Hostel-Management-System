"""Views of the Fees module (REQ-11 to REQ-16)."""
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import admin_required, student_required

from . import services
from .forms import FeeForm, PaymentForm


@admin_required
def overview(request):
    """Fees page: Record payment and Set fee forms, plus the outstanding dues table."""
    action = request.POST.get("action") if request.method == "POST" else None
    initial = {"student": request.GET.get("student")}
    # Prefixes keep the two forms' field names and HTML ids apart (payment-amount, fee-amount).
    payment_form = PaymentForm(
        request.POST if action == "record_payment" else None, initial=initial, prefix="payment"
    )
    fee_form = FeeForm(request.POST if action == "set_fee" else None, initial=initial, prefix="fee")

    if action == "record_payment" and payment_form.is_valid():
        student = payment_form.cleaned_data["student"]
        try:
            services.record_payment(
                student=student,
                amount=payment_form.cleaned_data["amount"],
                payment_date=payment_form.cleaned_data["payment_date"],
            )
        except services.FeeError as error:
            messages.error(request, str(error))
            if error.field:
                payment_form.add_error(error.field, error.hint)
        else:
            outstanding = services.rupees(services.get_outstanding(student))
            messages.success(
                request, f"Payment recorded for {student.name}. Outstanding balance: {outstanding}."
            )
            return redirect("fees:overview")

    if action == "set_fee" and fee_form.is_valid():
        student = fee_form.cleaned_data["student"]
        try:
            services.set_fee(student=student, amount=fee_form.cleaned_data["amount"])
        except services.FeeError as error:
            messages.error(request, str(error))
            if error.field:
                fee_form.add_error(error.field, error.hint)
        else:
            messages.success(request, f"Fee for {student.name} was saved.")
            return redirect("fees:overview")

    context = {
        "payment_form": payment_form,
        "fee_form": fee_form,
        "rows": services.fee_overview(),
    }
    return render(request, "fees/overview.html", context)


@admin_required
def student_detail(request, student_id):
    user_model = get_user_model()
    student = get_object_or_404(user_model, pk=student_id, role=user_model.Role.STUDENT)
    context = {"student": student, **services.fee_summary(student)}
    return render(request, "fees/student_detail.html", context)


@admin_required
def dues_report(request):
    """REQ-16: report of outstanding dues across all students."""
    hide_paid = request.GET.get("hide_paid") == "1"
    context = {"hide_paid": hide_paid, **services.dues_report(hide_paid=hide_paid)}
    return render(request, "fees/dues_report.html", context)


@student_required
def my_fees(request):
    """REQ-15: Fee Details page. A student only ever sees their own fees."""
    return render(request, "fees/my_fees.html", services.fee_summary(request.user))
