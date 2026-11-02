"""Tests for complaints and leave requests (REQ-17, REQ-19)."""
import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from complaints import services
from complaints.models import Complaint, LeaveRequest
from rooms.models import Block, Room
from rooms.services import allocate_student

User = get_user_model()
PAGE = "complaints:student_page"


def make_student(email="s1@example.com", srn="PES1UG24CS001"):
    return User.objects.create_user(
        email=email,
        password="Pass@1234x",
        name=email.split("@")[0],
        srn=srn,
        registration_status=User.Status.VERIFIED,
    )


class ComplaintTests(TestCase):
    def setUp(self):
        self.student = make_student()
        block = Block.objects.create(name="B1")
        self.room = Room.objects.create(block=block, room_number="101", room_type="Double", capacity=2)

    def test_student_with_room_files_complaint(self):
        """TC-REQ-01: complaint saved as Open and linked to the student's room."""
        allocate_student(student_id=self.student.pk, room_id=self.room.pk)
        complaint = services.file_complaint(student=self.student, description="Tap leaking")
        self.assertEqual(complaint.status, Complaint.Status.OPEN)
        self.assertEqual(complaint.room, self.room)

    def test_student_without_room_cannot_file_complaint(self):
        """Business rule: only a student with an allocated room can file a complaint."""
        with self.assertRaisesMessage(services.RequestError, "allocated room"):
            services.file_complaint(student=self.student, description="Tap leaking")
        self.assertFalse(Complaint.objects.exists())

    def test_empty_description_is_rejected(self):
        allocate_student(student_id=self.student.pk, room_id=self.room.pk)
        with self.assertRaises(services.RequestError):
            services.file_complaint(student=self.student, description="   ")

    def test_complaint_page_flow(self):
        """NFR-2 path: dashboard, Complaints & Leave page, submit, back on the same page."""
        allocate_student(student_id=self.student.pk, room_id=self.room.pk)
        self.client.force_login(self.student)
        response = self.client.post(
            reverse(PAGE), {"action": "complaint", "description": "Fan not working"}, follow=True
        )
        self.assertRedirects(response, reverse(PAGE))
        self.assertContains(response, "Your complaint was submitted and is Open.")
        self.assertContains(response, "Fan not working")
        self.assertContains(response, "New complaint (Room B1-101)")

    def test_empty_complaint_shows_field_error(self):
        allocate_student(student_id=self.student.pk, room_id=self.room.pk)
        self.client.force_login(self.student)
        response = self.client.post(reverse(PAGE), {"action": "complaint", "description": ""})
        self.assertContains(response, "Description is required.")
        self.assertFalse(Complaint.objects.exists())

    def test_page_without_room_hides_complaint_form(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse(PAGE))
        self.assertContains(response, "once a room has been allocated")
        response = self.client.post(reverse(PAGE), {"action": "complaint", "description": "Leak"})
        self.assertContains(response, "You need an allocated room")
        self.assertFalse(Complaint.objects.exists())

    def test_admin_sees_all_complaints(self):
        """REQ-17: the admin can view submitted complaints."""
        allocate_student(student_id=self.student.pk, room_id=self.room.pk)
        services.file_complaint(student=self.student, description="Light broken")
        admin = User.objects.create_superuser(email="a@example.com", password="Admin@2026", name="A")
        self.client.force_login(admin)
        response = self.client.get(reverse("complaints:admin_page"))
        self.assertContains(response, "Light broken")

    def test_student_cannot_open_admin_page(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse("complaints:admin_page"))
        self.assertEqual(response.status_code, 403)

    def test_student_sees_only_own_complaints(self):
        other = make_student("s2@example.com", "PES1UG24CS002")
        allocate_student(student_id=self.student.pk, room_id=self.room.pk)
        allocate_student(student_id=other.pk, room_id=self.room.pk)
        services.file_complaint(student=other, description="Other student's issue")
        self.client.force_login(self.student)
        response = self.client.get(reverse(PAGE))
        self.assertNotContains(response, "Other student&#x27;s issue")

    def test_dashboard_cards(self):
        allocate_student(student_id=self.student.pk, room_id=self.room.pk)
        services.file_complaint(student=self.student, description="Leak")
        self.client.force_login(self.student)
        response = self.client.get(reverse("accounts:student_dashboard"))
        self.assertContains(response, "Open complaints")
        admin = User.objects.create_superuser(email="a@example.com", password="Admin@2026", name="A")
        self.client.force_login(admin)
        response = self.client.get(reverse("accounts:admin_dashboard"))
        self.assertContains(response, "Open complaints")
        self.assertContains(response, "Pending leave")


class LeaveTests(TestCase):
    def setUp(self):
        self.student = make_student()

    def test_valid_leave_is_pending(self):
        """REQ-19: a valid request is saved with status Pending."""
        leave = services.submit_leave(
            student=self.student,
            start_date=datetime.date(2026, 11, 2),
            end_date=datetime.date(2026, 11, 4),
            reason="Family function",
        )
        self.assertEqual(leave.status, LeaveRequest.Status.PENDING)

    def test_end_before_start_is_rejected(self):
        """TC-REQ-03: end date before start date is refused and nothing is saved."""
        with self.assertRaisesMessage(services.RequestError, "End date cannot be before"):
            services.submit_leave(
                student=self.student,
                start_date=datetime.date(2026, 10, 20),
                end_date=datetime.date(2026, 10, 18),
                reason="Trip",
            )
        self.assertFalse(LeaveRequest.objects.exists())

    def test_same_day_leave_is_allowed(self):
        day = datetime.date(2026, 11, 2)
        leave = services.submit_leave(student=self.student, start_date=day, end_date=day, reason="Outing")
        self.assertEqual(leave.start_date, leave.end_date)

    def test_empty_reason_is_rejected(self):
        with self.assertRaises(services.RequestError):
            services.submit_leave(
                student=self.student,
                start_date=datetime.date(2026, 11, 2),
                end_date=datetime.date(2026, 11, 3),
                reason="",
            )

    def test_leave_page_flow_and_validation(self):
        self.client.force_login(self.student)
        response = self.client.post(
            reverse(PAGE),
            {"action": "leave", "start_date": "2026-10-20", "end_date": "2026-10-18", "reason": "Trip"},
        )
        self.assertContains(response, "End date cannot be before start date")
        self.assertFalse(LeaveRequest.objects.exists())
        response = self.client.post(
            reverse(PAGE),
            {"action": "leave", "start_date": "2026-11-02", "end_date": "2026-11-04", "reason": "Family function"},
            follow=True,
        )
        self.assertContains(response, "Your leave request was submitted and is Pending.")
        self.assertContains(response, "Family function")
