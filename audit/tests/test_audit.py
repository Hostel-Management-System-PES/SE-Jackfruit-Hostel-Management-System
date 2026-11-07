"""Tests for the audit log (SEC-6, TC-SEC-04)."""
from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts import services as account_services
from audit.models import AuditEntry
from fees import services as fee_services
from rooms import services as room_services
from rooms.models import Block, Room

User = get_user_model()
PASSWORD = "Pass@1234x"


def actions():
    return list(AuditEntry.objects.values_list("action", flat=True))


class AuditTestCase(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            email="admin@example.com", password="Admin@2026", name="Admin"
        )
        self.student = User.objects.create_user(
            email="asha@example.com",
            password=PASSWORD,
            name="Asha",
            srn="PES1UG24CS001",
            guardian_contact="9876543210",
            registration_status=User.Status.VERIFIED,
        )
        AuditEntry.objects.all().delete()


class LoginAuditTests(AuditTestCase):
    def test_successful_login_is_logged(self):
        self.client.post(reverse("accounts:login"), {"username": "asha@example.com", "password": PASSWORD})
        entry = AuditEntry.objects.get(action="login")
        self.assertEqual(entry.user, self.student)
        self.assertEqual(entry.identifier, "asha@example.com")
        self.assertEqual(entry.ip_address, "127.0.0.1")

    def test_failed_login_is_logged_without_password(self):
        """TC-SEC-04: a failed login is recorded with the typed identifier only."""
        self.client.post(reverse("accounts:login"), {"username": "asha@example.com", "password": "Wrong@9999"})
        entry = AuditEntry.objects.get(action="login_failed")
        self.assertIsNone(entry.user)
        self.assertEqual(entry.identifier, "asha@example.com")
        for value in AuditEntry.objects.values_list("identifier", "details"):
            self.assertNotIn("Wrong@9999", " ".join(value))

    def test_logout_is_logged(self):
        self.client.force_login(self.student)
        self.client.post(reverse("accounts:logout"))
        self.assertIn("logout", actions())


class ChangeAuditTests(AuditTestCase):
    def test_registration_decision_is_logged(self):
        pending = User.objects.create_user(
            email="ravi@example.com", password=PASSWORD, name="Ravi", srn="PES1UG24CS002"
        )
        account_services.decide_registration(user_id=pending.pk, decision=User.Status.VERIFIED)
        self.assertIn("registration", actions())

    def test_room_allocation_and_deallocation_are_logged(self):
        room = Room.objects.create(block=Block.objects.create(name="B1"), room_number="101", room_type="Single", capacity=1)
        allocation = room_services.allocate_student(student_id=self.student.pk, room_id=room.pk)
        room_services.deallocate_student(allocation_id=allocation.pk)
        self.assertIn("room_created", actions())
        self.assertIn("allocated", actions())
        self.assertIn("deallocated", actions())

    def test_fee_and_payment_are_logged(self):
        fee_services.set_fee(student=self.student, amount=Decimal("60000"))
        fee_services.record_payment(student=self.student, amount=Decimal("1000"), payment_date=date.today())
        self.assertIn("fee_set", actions())
        self.assertIn("payment", actions())

    def test_unchanged_fee_is_not_logged_twice(self):
        fee_services.set_fee(student=self.student, amount=Decimal("60000"))
        fee_services.set_fee(student=self.student, amount=Decimal("60000"))
        self.assertEqual(actions().count("fee_set"), 1)

    def test_action_done_in_a_request_records_the_admin(self):
        room = Room.objects.create(block=Block.objects.create(name="B1"), room_number="101", room_type="Single", capacity=1)
        AuditEntry.objects.all().delete()
        self.client.force_login(self.admin)
        self.client.post(reverse("rooms:allocate"), {"student": self.student.pk, "room": room.pk})
        entry = AuditEntry.objects.get(action="allocated")
        self.assertEqual(entry.user, self.admin)


class AccessDeniedAuditTests(AuditTestCase):
    def test_403_is_logged(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse("audit:log_list"))
        self.assertEqual(response.status_code, 403)
        entry = AuditEntry.objects.get(action="access_denied")
        self.assertEqual(entry.user, self.student)
        self.assertIn(reverse("audit:log_list"), entry.details)


class AuditPageTests(AuditTestCase):
    def test_admin_sees_log_and_can_filter(self):
        self.client.post(reverse("accounts:login"), {"username": "nobody@example.com", "password": "x"})
        self.client.force_login(self.admin)
        response = self.client.get(reverse("audit:log_list"))
        self.assertContains(response, "Audit Log")
        self.assertContains(response, "nobody@example.com")
        filtered = self.client.get(reverse("audit:log_list"), {"action": "logout"})
        self.assertNotContains(filtered, "nobody@example.com")

    def test_dashboard_shows_failed_login_card(self):
        self.client.post(reverse("accounts:login"), {"username": "asha@example.com", "password": "bad"})
        self.client.force_login(self.admin)
        response = self.client.get(reverse("accounts:admin_dashboard"))
        self.assertContains(response, "Failed logins (24h)")

    def test_menu_shows_audit_log_for_admin_only(self):
        self.client.force_login(self.admin)
        self.assertContains(self.client.get(reverse("accounts:admin_dashboard")), reverse("audit:log_list"))
        self.client.force_login(self.student)
        self.assertNotContains(self.client.get(reverse("accounts:student_dashboard")), reverse("audit:log_list"))

    def test_entries_cannot_be_changed_in_django_admin(self):
        self.client.force_login(self.admin)
        response = self.client.get("/django-admin/audit/auditentry/add/")
        self.assertEqual(response.status_code, 403)


class AuditDetailsTests(AuditTestCase):
    def test_money_is_shown_in_rupees(self):
        fee_services.set_fee(student=self.student, amount=Decimal("60000"))
        entry = AuditEntry.objects.get(action="fee_set")
        self.assertIn("₹ 60,000.00", entry.details)
