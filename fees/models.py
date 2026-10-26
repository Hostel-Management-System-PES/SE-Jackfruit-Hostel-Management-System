"""
Fee and payment records (REQ-11, REQ-12).

Field layout follows SRS Appendix B (Fee and PaymentRecord tables).
The outstanding balance is not stored: it is always calculated as
fee amount minus the sum of payments (REQ-13), so it can never go out of sync.
"""
import uuid
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

MIN_AMOUNT = Decimal("0.01")


class Fee(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # OneToOne: one fee record per student (REQ-11).
    student = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="fee"
    )
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(MIN_AMOUNT)]
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student}: {self.amount}"


class PaymentRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payments"
    )
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(MIN_AMOUNT)]
    )
    payment_date = models.DateField()
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-payment_date", "-recorded_at"]

    def __str__(self):
        return f"{self.student}: {self.amount} on {self.payment_date}"
