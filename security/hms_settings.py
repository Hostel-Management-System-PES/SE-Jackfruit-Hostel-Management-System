"""
Session settings added by the Security module (SEC-4).
hms/settings.py reads this file automatically when the security folder exists.
"""

# Log the user out after 30 minutes without any request.
SESSION_COOKIE_AGE = 30 * 60

# Every request restarts the 30-minute timer, so only idle sessions expire.
SESSION_SAVE_EVERY_REQUEST = True

# Closing the browser also ends the session.
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# JavaScript in the page cannot read the session cookie.
SESSION_COOKIE_HTTPONLY = True

# The session cookie is not sent with requests started by other websites.
SESSION_COOKIE_SAMESITE = "Lax"
