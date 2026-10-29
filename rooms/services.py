"""
Business rules of the Rooms module (REQ-7, REQ-8, REQ-10).

Other modules may call get_student_room() to find a student's room.
"""
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Count

from .models import Allocation, Room


class AllocationError(Exception):
    """A room allocation rule was broken. `field` names the form field at fault."""

    def __init__(self, message, field=None):
        super().__init__(message)
        self.field = field


def refresh_room_status(room):
    """REQ-10: Occupied when occupancy equals capacity, otherwise Vacant (SRS 3.1)."""
    occupied = room.allocations.count()
    new_status = Room.Status.OCCUPIED if occupied >= room.capacity else Room.Status.VACANT
    if room.status != new_status:
        room.status = new_status
        room.save(update_fields=["status"])
    return room


def allocate_student(*, student_id, room_id):
    """
    REQ-7, REQ-8, REQ-10: allocate a Verified student without a room to a room
    that is not full. The check and the save run in one transaction, and the
    room row is locked so two admins cannot fill the last bed at the same time.
    """
    user_model = get_user_model()
    with transaction.atomic():
        try:
            room = Room.objects.select_for_update().get(pk=room_id)
        except Room.DoesNotExist as exc:
            raise AllocationError("Room not found.", field="room") from exc
        try:
            student = user_model.objects.get(pk=student_id)
        except user_model.DoesNotExist as exc:
            raise AllocationError("Student not found.", field="student") from exc

        if student.role != user_model.Role.STUDENT:
            raise AllocationError("Only students can be allocated a room.", field="student")
        if student.registration_status != user_model.Status.VERIFIED:
            raise AllocationError(
                "Only verified students can be allocated a room.", field="student"
            )
        if Allocation.objects.filter(student=student).exists():
            raise AllocationError(f"{student.name} already has an allocated room.", field="student")
        occupied = room.allocations.count()
        if occupied >= room.capacity:
            raise AllocationError(
                f"Room {room} is full ({occupied} / {room.capacity}). The student was not allocated.",
                field="room",
            )

        allocation = Allocation.objects.create(student=student, room=room)
        refresh_room_status(room)
    return allocation


def get_student_room(student):
    """Return the student's allocated Room, or None if no room is allocated."""
    allocation = (
        Allocation.objects.select_related("room__block").filter(student=student).first()
    )
    return allocation.room if allocation else None


def rooms_with_occupancy():
    return (
        Room.objects.select_related("block")
        .annotate(occupied_count=Count("allocations"))
        .order_by("block__name", "room_number")
    )


def eligible_students():
    """Verified students who do not have a room yet."""
    user_model = get_user_model()
    return user_model.objects.filter(
        role=user_model.Role.STUDENT,
        registration_status=user_model.Status.VERIFIED,
        allocation__isnull=True,
    ).order_by("srn")


def current_allocations():
    return Allocation.objects.select_related("student", "room__block").annotate(
        occupied_count=Count("room__allocations")
    ).order_by("room__block__name", "room__room_number", "student__name")
