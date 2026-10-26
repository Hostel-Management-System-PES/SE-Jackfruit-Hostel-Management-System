from django.apps import AppConfig


class FeesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "fees"
    verbose_name = "Fee Management"

    # Menu entries shown in the left navigation (see hms/context_processors.py).
    hms_menu = [
        {"label": "Fees", "url_name": "fees:overview", "roles": ["Admin"], "order": 40},
    ]

    # Summary cards shown on the dashboards (see hms/dashboard.py).
    hms_dashboard_cards = [
        {"roles": ["Student"], "function": "fees.dashboard.student_fee_card", "order": 20},
    ]
