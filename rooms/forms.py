"""Forms for blocks, rooms and allocation (REQ-6, REQ-8)."""
from django import forms

from .models import Block, Room


class BlockForm(forms.ModelForm):
    class Meta:
        model = Block
        fields = ["name"]
        labels = {"name": "Block name"}

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if not name:
            raise forms.ValidationError("Block name is required.")
        duplicate = Block.objects.filter(name__iexact=name).exclude(pk=self.instance.pk)
        if duplicate.exists():
            raise forms.ValidationError("A block with this name already exists.")
        return name


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ["block", "room_number", "room_type", "capacity"]

    def clean_room_number(self):
        number = self.cleaned_data["room_number"].strip().upper()
        if not number:
            raise forms.ValidationError("Room number is required.")
        return number

    def clean_capacity(self):
        capacity = self.cleaned_data["capacity"]
        if capacity is None or capacity < 1:
            raise forms.ValidationError("Capacity must be at least 1.")
        if capacity > 10:
            raise forms.ValidationError("Capacity cannot be more than 10.")
        if self.instance.pk and capacity < self.instance.allocations.count():
            raise forms.ValidationError(
                "Capacity cannot be lower than the number of students already in the room."
            )
        return capacity

    def clean(self):
        cleaned = super().clean()
        block = cleaned.get("block")
        number = cleaned.get("room_number")
        if block and number:
            duplicate = Room.objects.filter(block=block, room_number__iexact=number)
            if duplicate.exclude(pk=self.instance.pk).exists():
                self.add_error("room_number", "This room number already exists in the block.")
        return cleaned


class StudentChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.srn} - {obj.name}"


class RoomChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj} ({obj.occupied_count} / {obj.capacity})"


class AllocationForm(forms.Form):
    student = StudentChoiceField(queryset=None, label="Student (verified only)")
    room = RoomChoiceField(queryset=None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .services import eligible_students, rooms_with_occupancy

        self.fields["student"].queryset = eligible_students()
        self.fields["room"].queryset = rooms_with_occupancy()
