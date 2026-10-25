"""
Root URL configuration.

Owner: P1. Each module's URLs are included automatically when the module is
enabled in settings (HMS_ENABLED_MODULES), under /<module>/.
"""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("", include("accounts.urls")),
]

for module in settings.HMS_ENABLED_MODULES:
    urlpatterns.append(path(f"{module}/", include(f"{module}.urls")))
