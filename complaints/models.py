"""
Complaints and leave requests (REQ-17 to REQ-20).

Field layout follows SRS Appendix B. All statuses are defined now, including
the ones Sprint 2 uses (In-progress, Resolved, Approved, Rejected), so the
database does not need to change in Sprint 2.
"""
import uuid

from django.conf import settings
from django.db import models


class Complaint(models.Model):
    class Status(models.TextChoices):
        OPEN = "Open", "Open"
        IN_PROGRESS = "In-progress", "In-progress"
        RESOLVED = "Resolved", "Resolved"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="complaints"
    )
    room = models.ForeignKey("rooms.Room", on_delete=models.PROTECT, related_name="complaints")
    description = models.TextField(max_length=1000)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student} ({self.room}): {self.status}"


class LeaveRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "Pending", "Pending"
        APPROVED = "Approved", "Approved"
        REJECTED = "Rejected", "Rejected"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="leave_requests"
    )
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField(max_length=500)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    decided_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student} {self.start_date} to {self.end_date}: {self.status}"
