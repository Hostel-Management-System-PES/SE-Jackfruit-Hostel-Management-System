from django.contrib import admin

from .models import Complaint, LeaveRequest


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ("student", "room", "status", "created_at")
    list_filter = ("status",)


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ("student", "start_date", "end_date", "status", "created_at")
    list_filter = ("status",)
