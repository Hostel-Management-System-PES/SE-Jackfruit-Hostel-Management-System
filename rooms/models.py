"""
Blocks, rooms and room allocations (REQ-6, REQ-8, REQ-10).

Field layout follows SRS Appendix B (Block and Room tables). The link between
a student and a room is stored here, in Allocation (one row per allocated
student), instead of a room_id column on the user table. This keeps the
Accounts module independent of the Rooms module.
"""
import uuid

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Block(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Room(models.Model):
    class RoomType(models.TextChoices):
        SINGLE = "Single", "Single"
        DOUBLE = "Double", "Double"
        TRIPLE = "Triple", "Triple"

    class Status(models.TextChoices):
        VACANT = "Vacant", "Vacant"
        OCCUPIED = "Occupied", "Occupied"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    block = models.ForeignKey(Block, on_delete=models.PROTECT, related_name="rooms")
    room_number = models.CharField(max_length=10)
    room_type = models.CharField(max_length=10, choices=RoomType.choices)
    capacity = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.VACANT)

    class Meta:
        ordering = ["block__name", "room_number"]
        constraints = [
            models.UniqueConstraint(fields=["block", "room_number"], name="unique_room_in_block"),
        ]

    def __str__(self):
        return f"{self.block.name}-{self.room_number}"

    @property
    def occupied(self):
        return self.allocations.count()


class Allocation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # OneToOne: a student has at most one allocated room (SRS 4.2).
    student = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="allocation"
    )
    room = models.ForeignKey(Room, on_delete=models.PROTECT, related_name="allocations")
    allocated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-allocated_at"]

    def __str__(self):
        return f"{self.student} -> {self.room}"
