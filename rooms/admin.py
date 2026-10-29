from django.contrib import admin

from .models import Allocation, Block, Room


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("__str__", "room_type", "capacity", "status")
    list_filter = ("block", "room_type", "status")


@admin.register(Allocation)
class AllocationAdmin(admin.ModelAdmin):
    list_display = ("student", "room", "allocated_at")
