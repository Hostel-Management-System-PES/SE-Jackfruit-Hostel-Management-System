"""Tests for registration and admin approval (REQ-1, REQ-2, REQ-3, SEC-1)."""
from django.test import TestCase
from django.urls import reverse

from accounts import services
from accounts.models import User

VALID_DATA = {
    "name": "Asha Rao",
    "email": "asha@example.com",
    "srn": "PES1UG24CS001",
    "guardian_contact": "9876543210",
    "password1": "Hostel@2026",
    "password2": "Hostel@2026",
}


class RegistrationTests(TestCase):
    def test_registration_creates_pending_student(self):
        """REQ-1, REQ-2: a new account is a Student in Pending state."""
        response = self.client.post(reverse("accounts:register"), VALID_DATA)
        self.assertRedirects(response, reverse("accounts:login"))
        user = User.objects.get(email="asha@example.com")
        self.assertEqual(user.role, User.Role.STUDENT)
        self.assertEqual(user.registration_status, User.Status.PENDING)
        self.assertEqual(user.srn, "PES1UG24CS001")

    def test_password_is_stored_hashed(self):
        """SEC-1: the raw password is never stored."""
        self.client.post(reverse("accounts:register"), VALID_DATA)
        user = User.objects.get(email="asha@example.com")
        self.assertNotEqual(user.password, "Hostel@2026")
        self.assertTrue(user.password.startswith("pbkdf2_"))
        self.assertTrue(user.check_password("Hostel@2026"))

    def test_duplicate_email_is_rejected(self):
        """TC-ACC-03: duplicate email (any letter case) is refused."""
        self.client.post(reverse("accounts:register"), VALID_DATA)
        data = {**VALID_DATA, "email": "ASHA@example.com", "srn": "PES1UG24CS002"}
        response = self.client.post(reverse("accounts:register"), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "already registered")
        self.assertEqual(User.objects.count(), 1)

    def test_duplicate_srn_is_rejected(self):
        """TC-ACC-03: duplicate SRN (any letter case) is refused."""
        self.client.post(reverse("accounts:register"), VALID_DATA)
        data = {**VALID_DATA, "email": "other@example.com", "srn": "pes1ug24cs001"}
        response = self.client.post(reverse("accounts:register"), data)
        self.assertContains(response, "already registered")
        self.assertEqual(User.objects.count(), 1)

    def test_invalid_fields_are_rejected(self):
        data = {**VALID_DATA, "guardian_contact": "abc", "password2": "Different@1"}
        response = self.client.post(reverse("accounts:register"), data)
        self.assertContains(response, "valid phone number")
        self.assertContains(response, "do not match")
        self.assertFalse(User.objects.exists())


class DecisionTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            email="admin@example.com", password="Admin@2026", name="Admin"
        )
        self.student = User.objects.create_user(
            email="s1@example.com", password="Student@2026", name="S One", srn="PES1UG24CS010"
        )

    def test_admin_approves_registration(self):
        """REQ-3: approve sets the status to Verified."""
        self.client.force_login(self.admin)
        url = reverse("accounts:decide_registration", args=[self.student.id])
        response = self.client.post(url, {"decision": "Verified"})
        self.assertRedirects(response, reverse("accounts:admin_dashboard"))
        self.student.refresh_from_db()
        self.assertEqual(self.student.registration_status, User.Status.VERIFIED)

    def test_admin_rejects_registration(self):
        """REQ-3: reject sets the status to Rejected."""
        services.decide_registration(user_id=self.student.id, decision="Rejected")
        self.student.refresh_from_db()
        self.assertEqual(self.student.registration_status, User.Status.REJECTED)

    def test_registration_cannot_be_decided_twice(self):
        services.decide_registration(user_id=self.student.id, decision="Verified")
        with self.assertRaises(services.AccountError):
            services.decide_registration(user_id=self.student.id, decision="Rejected")

    def test_invalid_decision_is_rejected(self):
        with self.assertRaises(services.AccountError):
            services.decide_registration(user_id=self.student.id, decision="Maybe")

    def test_admin_dashboard_lists_pending_students(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("accounts:admin_dashboard"))
        self.assertContains(response, "PES1UG24CS010")
