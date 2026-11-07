from django.contrib import admin

from .models import AuditEntry


@admin.register(AuditEntry)
class AuditEntryAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "action", "identifier", "details", "ip_address")
    list_filter = ("action",)
    search_fields = ("identifier", "details")

    # The audit log is read-only, even in the Django admin.
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
