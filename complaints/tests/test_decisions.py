"""Tests for admin complaint status updates and leave decisions (REQ-18, REQ-20, TC-REQ-02, TC-REQ-04)."""
import datetime
import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from complaints import services
from complaints.models import Complaint, LeaveRequest
from rooms.models import Block, Room
from rooms.services import allocate_student

User = get_user_model()
ADMIN_PAGE = "complaints:admin_page"


class DecisionTestCase(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            email="admin@example.com", password="Admin@2026", name="Admin"
        )
        self.student = User.objects.create_user(
            email="s1@example.com",
            password="Pass@1234x",
            name="Asha",
            srn="PES1UG24CS001",
            registration_status=User.Status.VERIFIED,
        )
        room = Room.objects.create(block=Block.objects.create(name="B1"), room_number="101", room_type="Double", capacity=2)
        allocate_student(student_id=self.student.pk, room_id=room.pk)
        self.complaint = services.file_complaint(student=self.student, description="Fan not working")
        self.leave = services.submit_leave(
            student=self.student,
            start_date=datetime.date(2026, 12, 1),
            end_date=datetime.date(2026, 12, 3),
            reason="Going home",
        )


class ComplaintStatusTests(DecisionTestCase):
    def status_url(self):
        return reverse("complaints:update_complaint_status", args=[self.complaint.pk])

    def test_admin_moves_complaint_through_statuses(self):
        """TC-REQ-02: Open -> In-progress -> Resolved, and the student sees Resolved."""
        self.client.force_login(self.admin)
        response = self.client.post(self.status_url(), {"status": "In-progress"}, follow=True)
        self.assertRedirects(response, reverse(ADMIN_PAGE))
        self.assertContains(response, "Complaint from Asha is now In-progress.")
        self.complaint.refresh_from_db()
        self.assertEqual(self.complaint.status, Complaint.Status.IN_PROGRESS)

        self.client.post(self.status_url(), {"status": "Resolved"})
        self.complaint.refresh_from_db()
        self.assertEqual(self.complaint.status, Complaint.Status.RESOLVED)

        self.client.force_login(self.student)
        page = self.client.get(reverse("complaints:student_page"))
        self.assertContains(page, "Resolved")

    def test_complaint_can_be_reopened(self):
        services.update_complaint_status(complaint_id=self.complaint.pk, status="Resolved")
        services.update_complaint_status(complaint_id=self.complaint.pk, status="Open")
        self.complaint.refresh_from_db()
        self.assertEqual(self.complaint.status, Complaint.Status.OPEN)

    def test_invalid_status_is_rejected(self):
        self.client.force_login(self.admin)
        response = self.client.post(self.status_url(), {"status": "Closed"}, follow=True)
        self.assertContains(response, "Choose a valid status")
        self.complaint.refresh_from_db()
        self.assertEqual(self.complaint.status, Complaint.Status.OPEN)

    def test_same_status_is_rejected(self):
        with self.assertRaisesMessage(services.RequestError, "already Open"):
            services.update_complaint_status(complaint_id=self.complaint.pk, status="Open")

    def test_unknown_complaint(self):
        with self.assertRaisesMessage(services.RequestError, "no longer exists"):
            services.update_complaint_status(complaint_id=uuid.uuid4(), status="Resolved")

    def test_buttons_show_the_other_statuses(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse(ADMIN_PAGE))
        self.assertContains(response, self.status_url())
        self.assertContains(response, 'value="In-progress"')
        self.assertContains(response, 'value="Resolved"')
        self.assertNotContains(response, 'name="status" value="Open"')

    def test_needs_post(self):
        self.client.force_login(self.admin)
        self.assertEqual(self.client.get(self.status_url()).status_code, 405)

    def test_student_cannot_change_status(self):
        self.client.force_login(self.student)
        response = self.client.post(self.status_url(), {"status": "Resolved"})
        self.assertEqual(response.status_code, 403)
        self.complaint.refresh_from_db()
        self.assertEqual(self.complaint.status, Complaint.Status.OPEN)

    def test_resolved_complaint_leaves_dashboard_count(self):
        services.update_complaint_status(complaint_id=self.complaint.pk, status="Resolved")
        self.assertEqual(services.unresolved_complaints().count(), 0)


class LeaveDecisionTests(DecisionTestCase):
    def decide_url(self):
        return reverse("complaints:decide_leave", args=[self.leave.pk])

    def test_approve_then_reject_is_refused(self):
        """TC-REQ-04: first decision saved, second refused, status stays Approved."""
        self.client.force_login(self.admin)
        response = self.client.post(self.decide_url(), {"decision": "Approved"}, follow=True)
        self.assertContains(response, "Leave request from Asha was approved.")
        self.leave.refresh_from_db()
        self.assertEqual(self.leave.status, LeaveRequest.Status.APPROVED)
        self.assertIsNotNone(self.leave.decided_at)

        response = self.client.post(self.decide_url(), {"decision": "Rejected"}, follow=True)
        self.assertContains(response, "This leave request was already approved.")
        self.leave.refresh_from_db()
        self.assertEqual(self.leave.status, LeaveRequest.Status.APPROVED)

        self.client.force_login(self.student)
        self.assertContains(self.client.get(reverse("complaints:student_page")), "Approved")

    def test_reject(self):
        leave = services.decide_leave(leave_id=self.leave.pk, decision="Rejected")
        self.assertEqual(leave.status, LeaveRequest.Status.REJECTED)

    def test_invalid_decision(self):
        with self.assertRaisesMessage(services.RequestError, "Choose Approve or Reject."):
            services.decide_leave(leave_id=self.leave.pk, decision="Pending")
        self.leave.refresh_from_db()
        self.assertEqual(self.leave.status, LeaveRequest.Status.PENDING)
        self.assertIsNone(self.leave.decided_at)

    def test_unknown_leave(self):
        with self.assertRaisesMessage(services.RequestError, "no longer exists"):
            services.decide_leave(leave_id=uuid.uuid4(), decision="Approved")

    def test_buttons_only_for_pending(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse(ADMIN_PAGE))
        self.assertContains(response, self.decide_url())
        self.assertContains(response, ">Approve</button>")
        services.decide_leave(leave_id=self.leave.pk, decision="Approved")
        response = self.client.get(reverse(ADMIN_PAGE))
        self.assertNotContains(response, self.decide_url())
        self.assertContains(response, "Decided")

    def test_student_cannot_decide(self):
        self.client.force_login(self.student)
        response = self.client.post(self.decide_url(), {"decision": "Approved"})
        self.assertEqual(response.status_code, 403)
        self.leave.refresh_from_db()
        self.assertEqual(self.leave.status, LeaveRequest.Status.PENDING)

    def test_needs_post(self):
        self.client.force_login(self.admin)
        self.assertEqual(self.client.get(self.decide_url()).status_code, 405)
