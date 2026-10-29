"""Views of the Rooms module (REQ-6, REQ-7, REQ-8, REQ-10)."""
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import NoReverseMatch, reverse

from accounts.decorators import admin_required, student_required

from . import services
from .forms import AllocationForm, BlockForm, RoomForm
from .models import Room

FIELD_HINTS = {
    "room": "Select a room that is not full.",
    "student": "Select a verified student without a room.",
}


@admin_required
def room_list(request):
    """Rooms & Blocks page: room table plus the Add room and Add block forms."""
    action = request.POST.get("action") if request.method == "POST" else None
    room_form = RoomForm(request.POST if action == "add_room" else None)
    block_form = BlockForm(request.POST if action == "add_block" else None)

    if action == "add_room" and room_form.is_valid():
        room = room_form.save()
        messages.success(request, f"Room {room} was added successfully.")
        return redirect("rooms:room_list")
    if action == "add_block" and block_form.is_valid():
        block = block_form.save()
        messages.success(request, f"Block {block.name} was added successfully.")
        return redirect("rooms:room_list")

    context = {
        "rooms": services.rooms_with_occupancy(),
        "room_form": room_form,
        "block_form": block_form,
    }
    return render(request, "rooms/room_list.html", context)


@admin_required
def room_edit(request, pk):
    room = get_object_or_404(Room, pk=pk)
    form = RoomForm(request.POST or None, instance=room)
    if request.method == "POST" and form.is_valid():
        room = form.save()
        services.refresh_room_status(room)
        messages.success(request, f"Room {room} was updated.")
        return redirect("rooms:room_list")
    return render(request, "rooms/room_form.html", {"form": form, "room": room})


@admin_required
def allocate(request):
    form = AllocationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        student = form.cleaned_data["student"]
        room = form.cleaned_data["room"]
        try:
            services.allocate_student(student_id=student.pk, room_id=room.pk)
        except services.AllocationError as error:
            messages.error(request, str(error))
            if error.field in FIELD_HINTS:
                form.add_error(error.field, FIELD_HINTS[error.field])
        else:
            messages.success(request, f"{student.name} was allocated to room {room}.")
            return redirect("rooms:allocate")
    context = {"form": form, "allocations": services.current_allocations()}
    return render(request, "rooms/allocate.html", context)


@student_required
def my_room(request):
    try:
        complaint_url = reverse("complaints:student_page")
    except NoReverseMatch:  # the Complaints module is not installed yet
        complaint_url = None
    context = {"room": services.get_student_room(request.user), "complaint_url": complaint_url}
    return render(request, "rooms/my_room.html", context)
