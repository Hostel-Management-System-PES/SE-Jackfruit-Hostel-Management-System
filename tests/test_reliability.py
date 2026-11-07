"""
NFR-3: an invalid or failed submission creates or changes no record, and
multi-step updates are saved in a single transaction.

The "failure in the middle" tests make a later step raise an error on purpose
(with mock.patch) and then check that the earlier step was rolled back too.
"""
from datetime import timedelta
from decimal import Decimal
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from complaints import services as complaint_services
from complaints.models import Complaint, LeaveRequest
from fees import services as fee_services
from fees.models import Fee, PaymentRecord
from rooms import services as room_services
from rooms.models import Allocation, Block, Room

User = get_user_model()


class ReliabilityTests(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            email="asha@example.com",
            password="Pass@1234x",
            name="Asha",
            srn="PES1UG24CS001",
            registration_status=User.Status.VERIFIED,
        )
        self.room = Room.objects.create(
            block=Block.objects.create(name="B1"), room_number="101", room_type="Single", capacity=1
        )
        self.today = timezone.localdate()

    # ---- Allocation with occupancy --------------------------------------------------

    def test_allocation_rolls_back_if_status_update_fails(self):
        with mock.patch.object(room_services, "refresh_room_status", side_effect=RuntimeError("crash")):
            with self.assertRaises(RuntimeError):
                room_services.allocate_student(student_id=self.student.pk, room_id=self.room.pk)
        self.assertFalse(Allocation.objects.exists())
        self.room.refresh_from_db()
        self.assertEqual(self.room.status, Room.Status.VACANT)

    def test_allocation_to_full_room_changes_nothing(self):
        room_services.allocate_student(student_id=self.student.pk, room_id=self.room.pk)
        other = User.objects.create_user(
            email="ravi@example.com", password="x", name="Ravi", srn="PES1UG24CS002",
            registration_status=User.Status.VERIFIED,
        )
        with self.assertRaises(room_services.AllocationError):
            room_services.allocate_student(student_id=other.pk, room_id=self.room.pk)
        self.assertEqual(Allocation.objects.count(), 1)

    # ---- Payment with balance ----------------------------------------------------------

    def test_payment_rolls_back_if_save_fails(self):
        fee_services.set_fee(student=self.student, amount=Decimal("1000"))
        with mock.patch.object(PaymentRecord.objects, "create", side_effect=RuntimeError("crash")):
            with self.assertRaises(RuntimeError):
                fee_services.record_payment(student=self.student, amount=Decimal("100"), payment_date=self.today)
        self.assertFalse(PaymentRecord.objects.exists())
        self.assertEqual(fee_services.get_outstanding(self.student), Decimal("1000"))

    def test_overpayment_changes_nothing(self):
        fee_services.set_fee(student=self.student, amount=Decimal("1000"))
        with self.assertRaises(fee_services.FeeError):
            fee_services.record_payment(student=self.student, amount=Decimal("1000.01"), payment_date=self.today)
        self.assertFalse(PaymentRecord.objects.exists())

    def test_future_payment_changes_nothing(self):
        fee_services.set_fee(student=self.student, amount=Decimal("1000"))
        with self.assertRaises(fee_services.FeeError):
            fee_services.record_payment(
                student=self.student, amount=Decimal("10"), payment_date=self.today + timedelta(days=1)
            )
        self.assertFalse(PaymentRecord.objects.exists())

    def test_fee_lower_than_paid_keeps_old_fee(self):
        fee_services.set_fee(student=self.student, amount=Decimal("1000"))
        fee_services.record_payment(student=self.student, amount=Decimal("800"), payment_date=self.today)
        with self.assertRaises(fee_services.FeeError):
            fee_services.set_fee(student=self.student, amount=Decimal("500"))
        self.assertEqual(Fee.objects.get(student=self.student).amount, Decimal("1000"))

    # ---- Complaints and leave ------------------------------------------------------------

    def test_complaint_without_room_creates_nothing(self):
        with self.assertRaises(complaint_services.RequestError):
            complaint_services.file_complaint(student=self.student, description="Fan broken")
        self.assertFalse(Complaint.objects.exists())

    def test_leave_with_bad_dates_creates_nothing(self):
        with self.assertRaises(complaint_services.RequestError):
            complaint_services.submit_leave(
                student=self.student,
                start_date=self.today,
                end_date=self.today - timedelta(days=2),
                reason="Home",
            )
        self.assertFalse(LeaveRequest.objects.exists())
