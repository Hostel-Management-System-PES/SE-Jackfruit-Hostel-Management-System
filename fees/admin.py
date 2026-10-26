from django.contrib import admin

from .models import Fee, PaymentRecord


@admin.register(Fee)
class FeeAdmin(admin.ModelAdmin):
    list_display = ("student", "amount", "updated_at")


@admin.register(PaymentRecord)
class PaymentRecordAdmin(admin.ModelAdmin):
    list_display = ("student", "amount", "payment_date", "recorded_at")
    list_filter = ("payment_date",)
