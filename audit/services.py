"""Writing and reading audit entries (SEC-6)."""
from datetime import timedelta

from django.utils import timezone

from .middleware import client_ip, get_current_request, get_current_user
from .models import AuditEntry


def log_event(*, action, details="", user=None, identifier="", request=None):
    """Write one audit entry. The user and IP default to the current request."""
    request = request or get_current_request()
    if user is None:
        user = get_current_user()
        if user is None and request is not None:
            candidate = getattr(request, "user", None)
            if candidate is not None and candidate.is_authenticated:
                user = candidate
    if not identifier and user is not None:
        identifier = user.email
    return AuditEntry.objects.create(
        user=user,
        identifier=identifier[:150],
        action=action,
        details=details[:255],
        ip_address=client_ip(request),
    )


def recent_entries(action=None):
    entries = AuditEntry.objects.select_related("user")
    if action:
        entries = entries.filter(action=action)
    return entries


def failed_logins_last_24h():
    since = timezone.now() - timedelta(hours=24)
    return AuditEntry.objects.filter(action=AuditEntry.Action.LOGIN_FAILED, timestamp__gte=since).count()
