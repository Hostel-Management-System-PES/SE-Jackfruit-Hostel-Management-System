"""
Business rules of the Fees module (REQ-11, REQ-12, REQ-13, REQ-14).

All money values are Decimal, never float, so there are no rounding errors.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from .models import Fee, PaymentRecord

ZERO = Decimal("0.00")


class FeeError(Exception):
    """A fee or payment rule was broken. `field` and `hint` describe it for the form."""

    def __init__(self, message, field=None, hint=None):
        super().__init__(message)
        self.field = field
        self.hint = hint or message


def rupees(amount):
    """Format an amount as Indian rupees, e.g. Rs 60000 -> '₹ 60,000.00'."""
    return f"₹ {amount:,.2f}"


def total_paid(student):
    """Sum of all payments recorded for the student."""
    result = PaymentRecord.objects.filter(student=student).aggregate(total=Sum("amount"))
    return result["total"] or ZERO


def get_outstanding(student):
    """REQ-13: outstanding = fee amount - total paid (0 if no fee is defined)."""
    fee = Fee.objects.filter(student=student).first()
    if fee is None:
        return ZERO
    return fee.amount - total_paid(student)


def set_fee(*, student, amount):
    """REQ-11: create or update the single fee record of a student."""
    amount = Decimal(amount)
    if amount <= 0:
        raise FeeError("Fee amount must be greater than 0.", field="amount")
    user_model = get_user_model()
    if student.role != user_model.Role.STUDENT:
        raise FeeError("Fees can only be set for students.", field="student")
    paid = total_paid(student)
    if amount < paid:
        raise FeeError(
            f"Fee cannot be lower than the amount already paid ({rupees(paid)}).",
            field="amount",
            hint="Fee cannot be lower than the amount already paid.",
        )
    fee, _created = Fee.objects.update_or_create(student=student, defaults={"amount": amount})
    return fee


def record_payment(*, student, amount, payment_date):
    """
    REQ-12, REQ-14: record a payment against a student.
    Rejected when the amount is not greater than 0, when no fee is defined,
    when the date is in the future, or when the amount exceeds the outstanding
    balance. A payment equal to the outstanding balance is accepted.
    """
    amount = Decimal(amount)
    if amount <= 0:
        raise FeeError("Payment amount must be greater than 0.", field="amount")
    if payment_date > timezone.localdate():
        raise FeeError("Payment date cannot be in the future.", field="payment_date")

    with transaction.atomic():
        # Lock the fee row so two payments recorded at the same time cannot both pass the check.
        fee = Fee.objects.select_for_update().filter(student=student).first()
        if fee is None:
            raise FeeError("No fee has been defined for this student yet.", field="student")
        outstanding = fee.amount - total_paid(student)
        if amount > outstanding:
            raise FeeError(
                f"Payment of {rupees(amount)} exceeds the outstanding balance of {rupees(outstanding)}.",
                field="amount",
                hint="Amount cannot exceed the outstanding balance.",
            )
        payment = PaymentRecord.objects.create(
            student=student, amount=amount, payment_date=payment_date
        )
    return payment


def fee_summary(student):
    """Fee, total paid, outstanding balance and payment history of one student."""
    fee = Fee.objects.filter(student=student).first()
    paid = total_paid(student)
    return {
        "fee": fee,
        "fee_amount": fee.amount if fee else None,
        "paid": paid,
        "outstanding": (fee.amount - paid) if fee else ZERO,
        "payments": PaymentRecord.objects.filter(student=student),
    }


def fee_overview():
    """One row per student with fee amount, paid and outstanding (admin overview)."""
    user_model = get_user_model()
    students = (
        user_model.objects.filter(role=user_model.Role.STUDENT)
        .select_related("fee")
        .annotate(paid_total=Sum("payments__amount"))
        .order_by("name")
    )
    rows = []
    for student in students:
        fee = getattr(student, "fee", None)
        paid = student.paid_total or ZERO
        rows.append(
            {
                "student": student,
                "fee_amount": fee.amount if fee else None,
                "paid": paid,
                "outstanding": (fee.amount - paid) if fee else None,
            }
        )
    return rows
