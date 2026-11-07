"""
Settings added by the Audit module (read at the end of hms/settings.py).

MIDDLEWARE_APPEND adds AuditMiddleware, which remembers who made each
request so signal handlers can record the user, and logs denied access.
"""
MIDDLEWARE_APPEND = ["audit.middleware.AuditMiddleware"]
