from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"
    verbose_name = "Accounts & Access"

    # Menu entries shown in the left navigation (see hms/context_processors.py).
    hms_menu = [
        {"label": "Dashboard", "url_name": "accounts:student_dashboard", "roles": ["Student"], "order": 10},
        {"label": "Dashboard", "url_name": "accounts:admin_dashboard", "roles": ["Admin"], "order": 10},
    ]

    # Summary cards shown on the dashboards (see hms/dashboard.py).
    hms_dashboard_cards = [
        {"roles": ["Admin"], "function": "accounts.dashboard.pending_registrations_card", "order": 10},
    ]
