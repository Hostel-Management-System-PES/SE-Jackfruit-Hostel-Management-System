from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "srn", "role", "registration_status", "created_at")
    list_filter = ("role", "registration_status")
    search_fields = ("name", "email", "srn")
    readonly_fields = ("password", "last_login", "created_at")
    ordering = ("name",)
