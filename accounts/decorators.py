"""
Role-based access control for views (REQ-4, SEC-2).

Every module protects its views with these decorators:
    @admin_required    only Verified Admins
    @student_required  only Verified Students
Anyone else gets a 403 page; anonymous users are sent to the login page.
"""
from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                return redirect_to_login(request.get_full_path())
            if not user.is_verified:
                raise PermissionDenied("Your account is not verified.")
            if roles and user.role not in roles:
                raise PermissionDenied("You do not have permission to open this page.")
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


admin_required = role_required("Admin")
student_required = role_required("Student")
