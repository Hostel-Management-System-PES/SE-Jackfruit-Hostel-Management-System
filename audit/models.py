"""
Audit log entries (SEC-6).

One row per security-relevant event: logins (successful and failed),
logouts, registration decisions, allocations, fee and payment changes,
complaint and leave decisions, and denied access. Passwords are never stored.
"""
from django.conf import settings
from django.db import models


class AuditEntry(models.Model):
    class Action(models.TextChoices):
        LOGIN = "login", "Login"
        LOGIN_FAILED = "login_failed", "Failed login"
        LOGOUT = "logout", "Logout"
        ACCESS_DENIED = "access_denied", "Access denied"
        REGISTRATION = "registration", "Registration decision"
        ROOM_CREATED = "room_created", "Room created"
        ALLOCATED = "allocated", "Room allocated"
        DEALLOCATED = "deallocated", "Room deallocated"
        FEE_SET = "fee_set", "Fee set"
        PAYMENT = "payment", "Payment recorded"
        COMPLAINT_STATUS = "complaint_status", "Complaint status changed"
        LEAVE_DECISION = "leave_decision", "Leave decision"

    # SET_NULL keeps the history even if the user account is deleted later.
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_entries",
    )
    # The email typed on the login form, or the email of the user who acted.
    identifier = models.CharField(max_length=150, blank=True)
    action = models.CharField(max_length=30, choices=Action.choices)
    details = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-timestamp", "-id"]
        verbose_name_plural = "audit entries"

    def __str__(self):
        return f"{self.timestamp:%Y-%m-%d %H:%M} {self.action} {self.identifier}"
