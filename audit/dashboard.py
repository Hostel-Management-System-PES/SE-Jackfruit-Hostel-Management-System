"""Dashboard summary card supplied by the Audit module."""
from . import services


def failed_logins_card(user):
    count = services.failed_logins_last_24h()
    return {
        "label": "Failed logins (24h)",
        "value": count,
        "badge": "Check log" if count >= 5 else None,
    }
