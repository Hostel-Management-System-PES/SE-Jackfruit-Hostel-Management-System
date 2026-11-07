"""
AuditMiddleware (SEC-6).

Remembers the current request for the length of the request, so signal
handlers (which do not receive the request) can record who did an action
and from which IP address. It also logs every 403 (PermissionDenied).
"""
import threading

from django.core.exceptions import PermissionDenied

_state = threading.local()


def get_current_request():
    return getattr(_state, "request", None)


def get_current_user():
    request = get_current_request()
    user = getattr(request, "user", None)
    if user is not None and user.is_authenticated:
        return user
    return None


def client_ip(request):
    if request is None:
        return None
    return request.META.get("REMOTE_ADDR") or None


class AuditMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _state.request = request
        try:
            return self.get_response(request)
        finally:
            _state.request = None

    def process_exception(self, request, exception):
        if isinstance(exception, PermissionDenied):
            from .services import log_event

            log_event(
                action="access_denied",
                details=f"{request.method} {request.path}"[:255],
                request=request,
            )
        return None  # let Django show the normal 403 page
