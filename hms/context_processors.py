"""
Builds the left navigation menu for every page.

Owner: P1. Each module declares its own menu entries in its apps.py as
`hms_menu`, so adding a page never requires editing this file or base.html.
Entry format: {"label": str, "url_name": str, "roles": [str], "order": int}.
"""
from django.apps import apps
from django.urls import NoReverseMatch, reverse


def navigation(request):
    user = getattr(request, "user", None)
    if user is None or not user.is_authenticated:
        return {"nav_items": []}

    items = []
    for config in apps.get_app_configs():
        for entry in getattr(config, "hms_menu", []):
            if user.role not in entry["roles"]:
                continue
            try:
                url = reverse(entry["url_name"])
            except NoReverseMatch:
                continue
            items.append(
                {
                    "label": entry["label"],
                    "url": url,
                    "order": entry.get("order", 100),
                    "active": request.path == url,
                }
            )
    items.sort(key=lambda item: item["order"])
    return {"nav_items": items}
