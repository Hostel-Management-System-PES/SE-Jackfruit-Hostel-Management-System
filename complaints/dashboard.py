"""Dashboard summary cards supplied by the Complaints & Leave module."""
from . import services


def student_complaints_card(user):
    open_complaints = services.unresolved_complaints().filter(student=user)
    latest = open_complaints.order_by("-created_at").first()
    return {
        "label": "Open complaints",
        "value": open_complaints.count(),
        "badge": latest.status if latest else None,
    }


def student_leave_card(user):
    pending = services.pending_leaves().filter(student=user).count()
    return {
        "label": "Leave requests",
        "value": pending,
        "badge": "Pending" if pending else None,
    }


def admin_complaints_card(user):
    return {"label": "Open complaints", "value": services.unresolved_complaints().count()}


def admin_leave_card(user):
    return {"label": "Pending leave", "value": services.pending_leaves().count()}
