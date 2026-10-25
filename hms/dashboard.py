"""
Collects the summary cards shown on the dashboards.

Owner: P1. Each module declares its own cards in its apps.py as
`hms_dashboard_cards`, pointing to a function in its own dashboard.py, so a
module adds its card without editing this file or the dashboard templates.
Entry format: {"roles": [str], "function": "module.dashboard.func", "order": int}.
The function receives the logged-in user and returns a card dict or None.
"""
from django.apps import apps
from django.utils.module_loading import import_string


def collect_cards(user):
    cards = []
    for config in apps.get_app_configs():
        for entry in getattr(config, "hms_dashboard_cards", []):
            if user.role not in entry["roles"]:
                continue
            card = import_string(entry["function"])(user)
            if card:
                cards.append({**card, "order": entry.get("order", 100)})
    cards.sort(key=lambda card: card["order"])
    return cards
