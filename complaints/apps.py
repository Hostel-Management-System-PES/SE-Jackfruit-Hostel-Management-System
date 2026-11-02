from django.apps import AppConfig


class ComplaintsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "complaints"
    verbose_name = "Complaints & Leave"

    # Menu entries shown in the left navigation (see hms/context_processors.py).
    hms_menu = [
        {"label": "Complaints & Leave", "url_name": "complaints:student_page", "roles": ["Student"], "order": 50},
        {"label": "Complaints & Leave", "url_name": "complaints:admin_page", "roles": ["Admin"], "order": 50},
    ]

    # Summary cards shown on the dashboards (see hms/dashboard.py).
    hms_dashboard_cards = [
        {"roles": ["Student"], "function": "complaints.dashboard.student_complaints_card", "order": 30},
        {"roles": ["Student"], "function": "complaints.dashboard.student_leave_card", "order": 40},
        {"roles": ["Admin"], "function": "complaints.dashboard.admin_complaints_card", "order": 30},
        {"roles": ["Admin"], "function": "complaints.dashboard.admin_leave_card", "order": 40},
    ]
