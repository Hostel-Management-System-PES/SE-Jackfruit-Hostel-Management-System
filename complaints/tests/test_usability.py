"""
NFR-2 / TC-USE-01: a student files a complaint in no more than 4 screens,
starting from the dashboard. The test follows the links a student would click
and counts every page shown.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from complaints.models import Complaint
from rooms.models import Block, Room
from rooms.services import allocate_student

User = get_user_model()
MAX_SCREENS = 4


class ComplaintScreenCountTests(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            email="new@example.com",
            password="Pass@1234x",
            name="New Student",
            srn="PES1UG24CS050",
            registration_status=User.Status.VERIFIED,
        )
        room = Room.objects.create(block=Block.objects.create(name="B1"), room_number="101", room_type="Double", capacity=2)
        allocate_student(student_id=self.student.pk, room_id=room.pk)
        self.client.force_login(self.student)

    def test_complaint_in_at_most_four_screens(self):
        screens = []

        # Screen 1: the dashboard, which has the Complaints & Leave menu link.
        dashboard = self.client.get(reverse("accounts:student_dashboard"))
        screens.append("dashboard")
        complaints_url = reverse("complaints:student_page")
        self.assertContains(dashboard, f'href="{complaints_url}"')

        # Screen 2: the Complaints & Leave page with the complaint form.
        page = self.client.get(complaints_url)
        screens.append("complaint form")
        self.assertContains(page, 'name="description"')

        # Screen 3: submit, which shows the confirmation on the same page.
        result = self.client.post(
            complaints_url, {"action": "complaint", "description": "Fan not working"}, follow=True
        )
        screens.append("confirmation")
        self.assertContains(result, "Your complaint was submitted and is Open.")

        self.assertTrue(Complaint.objects.filter(student=self.student).exists())
        self.assertLessEqual(len(screens), MAX_SCREENS)
        self.assertEqual(len(screens), 3)

    def test_my_room_page_also_links_to_complaints(self):
        """A second route: My Room -> Raise a complaint, still within 4 screens."""
        response = self.client.get(reverse("rooms:my_room"))
        self.assertContains(response, reverse("complaints:student_page"))
