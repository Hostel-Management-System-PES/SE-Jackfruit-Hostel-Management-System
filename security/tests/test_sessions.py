"""Tests for session expiry and rejection (SEC-4, TC-SEC-02)."""
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.test import TestCase
from django.urls import NoReverseMatch, reverse
from django.utils import timezone

User = get_user_model()
PASSWORD = "Pass@1234x"


def dues_url():
    """TC-SEC-02 opens the student's dues page (Fee Details)."""
    try:
        return reverse("fees:my_fees")
    except NoReverseMatch:  # the Fee Details page is not merged yet
        return reverse("accounts:student_dashboard")


class SessionSecurityTests(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            email="asha@example.com",
            password=PASSWORD,
            name="Asha",
            srn="PES1UG24CS001",
            registration_status=User.Status.VERIFIED,
        )

    def login(self):
        response = self.client.post(
            reverse("accounts:login"), {"username": "asha@example.com", "password": PASSWORD}
        )
        self.assertEqual(response.status_code, 302)
        return self.client.cookies[settings.SESSION_COOKIE_NAME].value

    def assert_sent_to_login(self, response):
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response["Location"].startswith(reverse("accounts:login")))

    def test_settings_are_applied(self):
        self.assertEqual(settings.SESSION_COOKIE_AGE, 1800)
        self.assertTrue(settings.SESSION_SAVE_EVERY_REQUEST)
        self.assertTrue(settings.SESSION_EXPIRE_AT_BROWSER_CLOSE)
        self.assertTrue(settings.SESSION_COOKIE_HTTPONLY)
        self.assertEqual(settings.SESSION_COOKIE_SAMESITE, "Lax")

    def test_logged_in_student_can_open_dues_page(self):
        self.login()
        self.assertEqual(self.client.get(dues_url()).status_code, 200)

    def test_expired_session_is_rejected(self):
        """TC-SEC-02: after the session expires, the dues page sends the user to login."""
        key = self.login()
        Session.objects.filter(session_key=key).update(expire_date=timezone.now() - timedelta(seconds=1))
        response = self.client.get(dues_url())
        self.assert_sent_to_login(response)

    def test_idle_timeout_is_30_minutes(self):
        key = self.login()
        expiry = Session.objects.get(session_key=key).expire_date
        remaining = expiry - timezone.now()
        self.assertGreater(remaining, timedelta(minutes=29))
        self.assertLessEqual(remaining, timedelta(minutes=30))

    def test_each_request_extends_the_session(self):
        key = self.login()
        Session.objects.filter(session_key=key).update(expire_date=timezone.now() + timedelta(minutes=5))
        self.client.get(dues_url())
        remaining = Session.objects.get(session_key=key).expire_date - timezone.now()
        self.assertGreater(remaining, timedelta(minutes=29))

    def test_session_is_deleted_on_logout_and_old_cookie_is_refused(self):
        key = self.login()
        self.client.post(reverse("accounts:logout"))
        self.assertFalse(Session.objects.filter(session_key=key).exists())
        # Someone who copied the old cookie tries to reuse it.
        self.client.cookies[settings.SESSION_COOKIE_NAME] = key
        self.assert_sent_to_login(self.client.get(dues_url()))

    def test_tampered_session_cookie_is_refused(self):
        self.login()
        self.client.cookies[settings.SESSION_COOKIE_NAME] = "forged-session-key-123456789"
        self.assert_sent_to_login(self.client.get(dues_url()))

    def test_session_cookie_is_httponly(self):
        self.login()
        cookie = self.client.cookies[settings.SESSION_COOKIE_NAME]
        self.assertTrue(cookie["httponly"])
        self.assertEqual(cookie["samesite"], "Lax")

    def test_new_session_key_after_login(self):
        """Session fixation: the key before login is not kept after login."""
        self.client.get(reverse("accounts:login"))
        session = self.client.session
        session["probe"] = "x"
        session.save()
        before = session.session_key
        after = self.login()
        self.assertNotEqual(before, after)
