from django.apps import AppConfig


class AuditConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "audit"
    verbose_name = "Audit Log"

    # Menu entry shown in the left navigation (see hms/context_processors.py).
    hms_menu = [
        {"label": "Audit Log", "url_name": "audit:log_list", "roles": ["Admin"], "order": 80},
    ]

    # Summary card shown on the admin dashboard (see hms/dashboard.py).
    hms_dashboard_cards = [
        {"roles": ["Admin"], "function": "audit.dashboard.failed_logins_card", "order": 60},
    ]

    def ready(self):
        # Connect the signal handlers that write audit entries (SEC-6).
        from . import signals  # noqa: F401
