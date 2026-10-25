"""Tests for login and role-based access (REQ-21, REQ-4, REQ-2)."""
from django.test import TestCase
from django.urls import reverse

from accounts.models import User


class LoginTests(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            email="student1@example.com",
            password="Pass@1234x",
            name="Student One",
            srn="PES1UG24CS100",
            registration_status=User.Status.VERIFIED,
        )
        self.admin = User.objects.create_superuser(
            email="admin@example.com", password="Admin@2026", name="Admin"
        )

    def login(self, identifier, password):
        return self.client.post(
            reverse("accounts:login"), {"username": identifier, "password": password}
        )

    def test_verified_student_logs_in_with_email(self):
        """TC-ACC-01: valid login reaches the student dashboard."""
        response = self.login("student1@example.com", "Pass@1234x")
        self.assertRedirects(
            response, reverse("accounts:home"), target_status_code=302
        )
        response = self.client.get(reverse("accounts:home"))
        self.assertRedirects(response, reverse("accounts:student_dashboard"))

    def test_verified_student_logs_in_with_srn(self):
        """REQ-21: SRN works as the login identifier, in any letter case."""
        self.login("pes1ug24cs100", "Pass@1234x")
        response = self.client.get(reverse("accounts:student_dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_admin_lands_on_admin_dashboard(self):
        self.login("admin@example.com", "Admin@2026")
        response = self.client.get(reverse("accounts:home"))
        self.assertRedirects(response, reverse("accounts:admin_dashboard"))

    def test_wrong_password_is_rejected(self):
        """TC-ACC-02: wrong password shows an error and creates no session."""
        response = self.login("student1@example.com", "wrongpass")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid credentials")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_pending_account_cannot_log_in(self):
        """TC-ACC-04: a Pending account is refused until approved."""
        User.objects.create_user(
            email="new@example.com", password="Pass@1234x", name="New", srn="PES1UG24CS101"
        )
        response = self.login("new@example.com", "Pass@1234x")
        self.assertContains(response, "pending admin approval")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_rejected_account_cannot_log_in(self):
        User.objects.create_user(
            email="rej@example.com",
            password="Pass@1234x",
            name="Rejected",
            srn="PES1UG24CS102",
            registration_status=User.Status.REJECTED,
        )
        response = self.login("rej@example.com", "Pass@1234x")
        self.assertContains(response, "rejected")


class AccessControlTests(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            email="student1@example.com",
            password="Pass@1234x",
            name="Student One",
            srn="PES1UG24CS100",
            registration_status=User.Status.VERIFIED,
        )
        self.admin = User.objects.create_superuser(
            email="admin@example.com", password="Admin@2026", name="Admin"
        )

    def test_student_cannot_open_admin_dashboard(self):
        """TC-SEC-01: a student gets 403 on an admin page."""
        self.client.force_login(self.student)
        response = self.client.get(reverse("accounts:admin_dashboard"))
        self.assertEqual(response.status_code, 403)

    def test_student_cannot_approve_registrations(self):
        self.client.force_login(self.student)
        url = reverse("accounts:decide_registration", args=[self.student.id])
        response = self.client.post(url, {"decision": "Verified"})
        self.assertEqual(response.status_code, 403)

    def test_admin_cannot_open_student_dashboard(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("accounts:student_dashboard"))
        self.assertEqual(response.status_code, 403)

    def test_anonymous_user_is_sent_to_login(self):
        response = self.client.get(reverse("accounts:admin_dashboard"))
        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('accounts:admin_dashboard')}",
        )

    def test_logout_ends_session(self):
        self.client.force_login(self.student)
        self.client.post(reverse("accounts:logout"))
        self.assertNotIn("_auth_user_id", self.client.session)
