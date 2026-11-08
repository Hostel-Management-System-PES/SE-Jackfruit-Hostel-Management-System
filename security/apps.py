from django.apps import AppConfig


class SecurityConfig(AppConfig):
    """
    SEC-4: session rules. This module has no pages; its settings live in
    hms_settings.py, which hms/settings.py reads automatically.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "security"
    verbose_name = "Session Security"
