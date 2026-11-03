"""Business rules of the Complaints & Leave module (REQ-17, REQ-19)."""
from rooms.services import get_student_room

from .models import Complaint, LeaveRequest

MAX_DESCRIPTION = 1000
MAX_REASON = 500


class RequestError(Exception):
    """A complaint or leave rule was broken. `field` names the form field at fault."""

    def __init__(self, message, field=None):
        super().__init__(message)
        self.field = field


def file_complaint(*, student, description):
    """REQ-17: a student with an allocated room files a complaint; it starts as Open."""
    description = (description or "").strip()
    if not description:
        raise RequestError("Description is required.", field="description")
    if len(description) > MAX_DESCRIPTION:
        raise RequestError(
            f"Description cannot be longer than {MAX_DESCRIPTION} characters.", field="description"
        )
    room = get_student_room(student)
    if room is None:
        raise RequestError("You need an allocated room before you can file a complaint.")
    return Complaint.objects.create(
        student=student, room=room, description=description, status=Complaint.Status.OPEN
    )


def submit_leave(*, student, start_date, end_date, reason):
    """REQ-19: a student requests leave; end date must not be before start date."""
    reason = (reason or "").strip()
    if not reason:
        raise RequestError("Reason is required.", field="reason")
    if len(reason) > MAX_REASON:
        raise RequestError(f"Reason cannot be longer than {MAX_REASON} characters.", field="reason")
    if start_date is None or end_date is None:
        raise RequestError("Start date and end date are required.")
    if end_date < start_date:
        raise RequestError("End date cannot be before start date.", field="end_date")
    return LeaveRequest.objects.create(
        student=student,
        start_date=start_date,
        end_date=end_date,
        reason=reason,
        status=LeaveRequest.Status.PENDING,
    )


def student_complaints(student):
    return Complaint.objects.filter(student=student).select_related("room__block")


def student_leaves(student):
    return LeaveRequest.objects.filter(student=student)


def all_complaints():
    return Complaint.objects.select_related("student", "room__block")


def all_leaves():
    return LeaveRequest.objects.select_related("student")


def unresolved_complaints():
    return Complaint.objects.exclude(status=Complaint.Status.RESOLVED)


def pending_leaves():
    return LeaveRequest.objects.filter(status=LeaveRequest.Status.PENDING)
