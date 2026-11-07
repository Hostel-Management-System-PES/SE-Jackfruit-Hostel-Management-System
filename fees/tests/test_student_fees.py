"""Tests for the student Fee Details page and the admin Dues Report (REQ-15, REQ-16, TC-FEE-03)."""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from fees import services

User = get_user_model()


def make_student(email, srn, name):
    return User.objects.create_user(
        email=email,
        password="Pass@1234x",
        name=name,
        srn=srn,
        registration_status=User.Status.VERIFIED,
    )


class FeesTestCase(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            email="admin@example.com", password="Admin@2026", name="Admin"
        )
        self.s1 = make_student("s1@example.com", "PES1UG24CS001", "Asha")
        self.s2 = make_student("s2@example.com", "PES1UG24CS002", "Ravi")
        self.s3 = make_student("s3@example.com", "PES1UG24CS003", "Meera")
        today = timezone.localdate()
        services.set_fee(student=self.s1, amount=Decimal("60000"))
        services.record_payment(student=self.s1, amount=Decimal("20000"), payment_date=today)
        services.record_payment(student=self.s1, amount=Decimal("15000"), payment_date=today)
        services.set_fee(student=self.s2, amount=Decimal("50000"))
        services.record_payment(student=self.s2, amount=Decimal("50000"), payment_date=today)
        # s3 has no fee yet


class MyFeesTests(FeesTestCase):
    def test_student_sees_own_fee_payments_and_outstanding(self):
        """TC-FEE-03 step 1: own fee, payments and outstanding are shown."""
        self.client.force_login(self.s1)
        response = self.client.get(reverse("fees:my_fees"))
        self.assertContains(response, "Fee Details")
        self.assertContains(response, "₹ 60,000.00")
        self.assertContains(response, "₹ 35,000.00")  # total paid
        self.assertContains(response, "₹ 25,000.00")  # outstanding
        self.assertContains(response, "₹ 20,000.00")
        self.assertContains(response, "₹ 15,000.00")
        self.assertContains(response, "badge-due")

    def test_student_never_sees_another_students_fees(self):
        self.client.force_login(self.s1)
        response = self.client.get(reverse("fees:my_fees"))
        self.assertNotContains(response, "₹ 50,000.00")

    def test_other_students_detail_page_is_refused(self):
        """TC-FEE-03 step 2: changing the URL to S2's dues gives 403."""
        self.client.force_login(self.s1)
        response = self.client.get(reverse("fees:student_detail", args=[self.s2.pk]))
        self.assertEqual(response.status_code, 403)

    def test_fully_paid_student_sees_paid_badge(self):
        self.client.force_login(self.s2)
        response = self.client.get(reverse("fees:my_fees"))
        self.assertContains(response, "badge-paid")
        self.assertContains(response, "₹ 0.00")

    def test_student_without_fee_sees_message(self):
        self.client.force_login(self.s3)
        response = self.client.get(reverse("fees:my_fees"))
        self.assertContains(response, "No fee has been set for you yet.")

    def test_menu_has_fee_details_for_students(self):
        self.client.force_login(self.s1)
        response = self.client.get(reverse("accounts:student_dashboard"))
        self.assertContains(response, reverse("fees:my_fees"))

    def test_admin_cannot_open_student_fee_page(self):
        self.client.force_login(self.admin)
        self.assertEqual(self.client.get(reverse("fees:my_fees")).status_code, 403)


class DuesReportTests(FeesTestCase):
    def test_report_totals(self):
        report = services.dues_report()
        self.assertEqual(report["totals"]["fee"], Decimal("110000"))
        self.assertEqual(report["totals"]["paid"], Decimal("85000"))
        self.assertEqual(report["totals"]["outstanding"], Decimal("25000"))
        self.assertEqual(report["totals"]["with_dues"], 1)
        self.assertEqual(report["no_fee"], [self.s3])

    def test_largest_balance_first(self):
        rows = services.dues_report()["rows"]
        self.assertEqual([row["student"] for row in rows], [self.s1, self.s2])

    def test_hide_paid_filter(self):
        rows = services.dues_report(hide_paid=True)["rows"]
        self.assertEqual([row["student"] for row in rows], [self.s1])

    def test_admin_page(self):
        """REQ-16: admin sees the report with totals and the students without a fee."""
        self.client.force_login(self.admin)
        response = self.client.get(reverse("fees:dues_report"))
        self.assertContains(response, "Dues Report")
        self.assertContains(response, "₹ 110,000.00")
        self.assertContains(response, "Asha")
        self.assertContains(response, "Ravi")
        self.assertContains(response, "Students without a fee")
        self.assertContains(response, "Meera")

    def test_admin_page_hide_paid(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("fees:dues_report"), {"hide_paid": "1"})
        self.assertContains(response, "Asha")
        self.assertNotContains(response, "PES1UG24CS002")
        self.assertContains(response, "Show all students")

    def test_menu_has_dues_report_for_admin(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("accounts:admin_dashboard"))
        self.assertContains(response, reverse("fees:dues_report"))

    def test_student_cannot_open_report(self):
        self.client.force_login(self.s1)
        self.assertEqual(self.client.get(reverse("fees:dues_report")).status_code, 403)
