"""Dashboard summary cards supplied by the Rooms module."""
from .models import Room
from .services import get_student_room


def student_room_card(user):
    room = get_student_room(user)
    if room is None:
        return {"label": "Allocated room", "value": "Not allocated"}
    return {
        "label": "Allocated room",
        "value": str(room),
        "sub": f"Block {room.block.name}",
        "badge": room.status,
    }


def admin_rooms_card(user):
    total = Room.objects.count()
    vacant = Room.objects.filter(status=Room.Status.VACANT).count()
    return {"label": "Rooms vacant / total", "value": f"{vacant} / {total}"}
