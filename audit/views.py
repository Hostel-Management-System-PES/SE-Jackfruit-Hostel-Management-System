"""Audit Log page for admins (SEC-6)."""
from django.core.paginator import Paginator
from django.shortcuts import render

from accounts.decorators import admin_required

from . import services
from .models import AuditEntry


@admin_required
def log_list(request):
    action = request.GET.get("action", "")
    if action not in AuditEntry.Action.values:
        action = ""
    paginator = Paginator(services.recent_entries(action or None), 50)
    page = paginator.get_page(request.GET.get("page"))
    context = {
        "page": page,
        "action": action,
        "actions": AuditEntry.Action.choices,
    }
    return render(request, "audit/log_list.html", context)
