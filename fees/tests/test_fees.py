"""Tests for fees and payments (REQ-11, REQ-12, REQ-13, REQ-14)."""
import datetime
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from fees import services
from fees.models import Fee, PaymentRecord

User = get_user_model()


def make_student(email="s1@example.com", srn="PES1UG24CS001"):
    return User.objects.create_user(
        email=email,
        password="Pass@1234x",
        name=email.split("@")[0],
        srn=srn,
        registration_status=User.Status.VERIFIED,
    )


class FeeServiceTests(TestCase):
    def setUp(self):
        self.student = make_student()
        self.today = timezone.localdate()

    def test_set_fee_creates_one_record_per_student(self):
        """REQ-11: setting the fee again updates the same record."""
        services.set_fee(student=self.student, amount=Decimal("50000"))
        services.set_fee(student=self.student, amount=Decimal("55000"))
        self.assertEqual(Fee.objects.filter(student=self.student).count(), 1)
        self.assertEqual(Fee.objects.get(student=self.student).amount, Decimal("55000"))

    def test_fee_must_be_positive(self):
        """REQ-11: amount must be greater than 0."""
        for amount in (Decimal("0"), Decimal("-100")):
            with self.assertRaises(services.FeeError):
                services.set_fee(student=self.student, amount=amount)
        self.assertFalse(Fee.objects.exists())

    def test_fee_cannot_be_set_for_admin(self):
        admin = User.objects.create_superuser(email="a@example.com", password="Admin@2026", name="A")
        with self.assertRaises(services.FeeError):
            services.set_fee(student=admin, amount=Decimal("100"))

    def test_payment_reduces_outstanding(self):
        """TC-FEE-01: fee 50000, payment 20000, outstanding 30000."""
        services.set_fee(student=self.student, amount=Decimal("50000"))
        services.record_payment(student=self.student, amount=Decimal("20000"), payment_date=self.today)
        self.assertEqual(services.get_outstanding(self.student), Decimal("30000"))
        self.assertEqual(services.total_paid(self.student), Decimal("20000"))

    def test_outstanding_is_zero_without_fee(self):
        """REQ-13: no fee defined means nothing outstanding."""
        self.assertEqual(services.get_outstanding(self.student), Decimal("0"))

    def test_payment_above_outstanding_is_rejected_exact_amount_accepted(self):
        """TC-FEE-02: 30001 refused with no record; exactly 30000 accepted."""
        services.set_fee(student=self.student, amount=Decimal("50000"))
        services.record_payment(student=self.student, amount=Decimal("20000"), payment_date=self.today)
        with self.assertRaisesMessage(services.FeeError, "exceeds the outstanding balance"):
            services.record_payment(student=self.student, amount=Decimal("30001"), payment_date=self.today)
        self.assertEqual(PaymentRecord.objects.count(), 1)
        services.record_payment(student=self.student, amount=Decimal("30000"), payment_date=self.today)
        self.assertEqual(services.get_outstanding(self.student), Decimal("0"))

    def test_zero_or_negative_payment_is_rejected(self):
        """REQ-14: a payment must be greater than 0."""
        services.set_fee(student=self.student, amount=Decimal("1000"))
        for amount in (Decimal("0"), Decimal("-5")):
            with self.assertRaises(services.FeeError):
                services.record_payment(student=self.student, amount=amount, payment_date=self.today)
        self.assertFalse(PaymentRecord.objects.exists())

    def test_payment_without_fee_is_rejected(self):
        with self.assertRaisesMessage(services.FeeError, "No fee"):
            services.record_payment(student=self.student, amount=Decimal("10"), payment_date=self.today)

    def test_future_payment_date_is_rejected(self):
        services.set_fee(student=self.student, amount=Decimal("1000"))
        tomorrow = self.today + datetime.timedelta(days=1)
        with self.assertRaises(services.FeeError):
            services.record_payment(student=self.student, amount=Decimal("10"), payment_date=tomorrow)

    def test_fee_cannot_drop_below_amount_paid(self):
        services.set_fee(student=self.student, amount=Decimal("1000"))
        services.record_payment(student=self.student, amount=Decimal("800"), payment_date=self.today)
        with self.assertRaises(services.FeeError):
            services.set_fee(student=self.student, amount=Decimal("500"))

    def test_fee_overview_lists_every_student(self):
        other = make_student("s2@example.com", "PES1UG24CS002")
        services.set_fee(student=self.student, amount=Decimal("1000"))
        rows = {row["student"]: row for row in services.fee_overview()}
        self.assertEqual(rows[self.student]["outstanding"], Decimal("1000"))
        self.assertIsNone(rows[other]["fee_amount"])


class FeeViewTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            email="admin@example.com", password="Admin@2026", name="Admin"
        )
        self.student = make_student()
        self.today = timezone.localdate()
        self.url = reverse("fees:overview")

    def record(self, amount):
        return self.client.post(
            self.url,
            {
                "action": "record_payment",
                "payment-student": self.student.pk,
                "payment-amount": amount,
                "payment-payment_date": self.today.isoformat(),
            },
        )

    def test_admin_sets_fee_and_records_payment(self):
        """TC-FEE-01 through the Fees page."""
        self.client.force_login(self.admin)
        response = self.client.post(
            self.url, {"action": "set_fee", "fee-student": self.student.pk, "fee-amount": "50000"}
        )
        self.assertRedirects(response, self.url)
        response = self.client.post(
            self.url,
            {
                "action": "record_payment",
                "payment-student": self.student.pk,
                "payment-amount": "20000",
                "payment-payment_date": self.today.isoformat(),
            },
            follow=True,
        )
        self.assertRedirects(response, self.url)
        self.assertContains(response, "Outstanding balance: ₹ 30,000.00")
        self.assertContains(response, "30,000.00")
        detail = self.client.get(reverse("fees:student_detail", args=[self.student.pk]))
        self.assertContains(detail, "₹ 20,000.00")

    def test_overpayment_shows_banner_and_field_error(self):
        """TC-FEE-02 through the Fees page: red banner, error under Amount, no record."""
        services.set_fee(student=self.student, amount=Decimal("1000"))
        self.client.force_login(self.admin)
        response = self.record("1000.01")
        self.assertContains(response, "Payment of ₹ 1,000.01 exceeds the outstanding balance of ₹ 1,000.00.")
        self.assertContains(response, "Amount cannot exceed the outstanding balance.")
        self.assertFalse(PaymentRecord.objects.exists())

    def test_zero_amount_is_rejected_by_form(self):
        services.set_fee(student=self.student, amount=Decimal("1000"))
        self.client.force_login(self.admin)
        response = self.record("0")
        self.assertContains(response, "greater than 0")
        self.assertFalse(PaymentRecord.objects.exists())

    def test_payment_form_lists_only_students_with_fee(self):
        other = make_student("s2@example.com", "PES1UG24CS002")
        services.set_fee(student=self.student, amount=Decimal("1000"))
        self.client.force_login(self.admin)
        response = self.client.get(self.url)
        form = response.context["payment_form"]
        self.assertIn(self.student, form.fields["student"].queryset)
        self.assertNotIn(other, form.fields["student"].queryset)

    def test_overview_lists_students(self):
        self.client.force_login(self.admin)
        response = self.client.get(self.url)
        self.assertContains(response, "PES1UG24CS001")
        self.assertContains(response, "Not set")

    def test_student_dashboard_shows_outstanding_card(self):
        """REQ-13: the student sees the outstanding balance on the dashboard."""
        services.set_fee(student=self.student, amount=Decimal("60000"))
        services.record_payment(student=self.student, amount=Decimal("35000"), payment_date=self.today)
        self.client.force_login(self.student)
        response = self.client.get(reverse("accounts:student_dashboard"))
        self.assertContains(response, "Outstanding fee")
        self.assertContains(response, "₹ 25,000.00")
        self.assertContains(response, "of ₹ 60,000.00")

    def test_student_cannot_open_fee_admin_pages(self):
        """SEC-2: fee administration is admin-only."""
        self.client.force_login(self.student)
        self.assertEqual(self.client.get(self.url).status_code, 403)
        url = reverse("fees:student_detail", args=[self.student.pk])
        self.assertEqual(self.client.get(url).status_code, 403)
