"""Dashboard summary cards supplied by the Accounts module."""
from . import services


def pending_registrations_card(user):
    return {"label": "Pending registrations", "value": services.pending_students().count()}
