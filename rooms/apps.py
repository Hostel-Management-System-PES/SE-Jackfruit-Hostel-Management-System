from django.apps import AppConfig


class RoomsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "rooms"
    verbose_name = "Room & Allocation"

    # Menu entries shown in the left navigation (see hms/context_processors.py).
    hms_menu = [
        {"label": "Rooms & Blocks", "url_name": "rooms:room_list", "roles": ["Admin"], "order": 20},
        {"label": "Room Allocation", "url_name": "rooms:allocate", "roles": ["Admin"], "order": 25},
        {"label": "My Room", "url_name": "rooms:my_room", "roles": ["Student"], "order": 20},
    ]

    # Summary cards shown on the dashboards (see hms/dashboard.py).
    hms_dashboard_cards = [
        {"roles": ["Student"], "function": "rooms.dashboard.student_room_card", "order": 10},
        {"roles": ["Admin"], "function": "rooms.dashboard.admin_rooms_card", "order": 20},
    ]
