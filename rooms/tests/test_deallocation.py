"""Tests for deallocating a student from a room (REQ-9, REQ-10, TC-ROOM-04)."""
import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rooms import services
from rooms.models import Allocation, Block, Room

User = get_user_model()


def make_student(email, srn):
    return User.objects.create_user(
        email=email,
        password="Pass@1234x",
        name=email.split("@")[0],
        srn=srn,
        registration_status=User.Status.VERIFIED,
    )


class DeallocationTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            email="admin@example.com", password="Admin@2026", name="Admin"
        )
        block = Block.objects.create(name="B1")
        self.room = Room.objects.create(block=block, room_number="101", room_type="Double", capacity=2)
        self.s1 = make_student("s1@example.com", "PES1UG24CS001")
        self.s2 = make_student("s2@example.com", "PES1UG24CS002")

    def test_deallocate_reduces_occupancy(self):
        """TC-ROOM-04: allocation removed and occupancy goes down."""
        allocation = services.allocate_student(student_id=self.s1.pk, room_id=self.room.pk)
        student, room = services.deallocate_student(allocation_id=allocation.pk)
        self.assertEqual(student, self.s1)
        self.assertEqual(room.occupied, 0)
        self.assertIsNone(services.get_student_room(self.s1))

    def test_full_room_becomes_vacant_after_deallocation(self):
        """REQ-10: status goes back to Vacant when a bed is freed."""
        a1 = services.allocate_student(student_id=self.s1.pk, room_id=self.room.pk)
        services.allocate_student(student_id=self.s2.pk, room_id=self.room.pk)
        self.room.refresh_from_db()
        self.assertEqual(self.room.status, Room.Status.OCCUPIED)
        services.deallocate_student(allocation_id=a1.pk)
        self.room.refresh_from_db()
        self.assertEqual(self.room.status, Room.Status.VACANT)
        self.assertEqual(self.room.occupied, 1)

    def test_deallocated_student_can_be_allocated_again(self):
        allocation = services.allocate_student(student_id=self.s1.pk, room_id=self.room.pk)
        services.deallocate_student(allocation_id=allocation.pk)
        services.allocate_student(student_id=self.s1.pk, room_id=self.room.pk)
        self.assertEqual(services.get_student_room(self.s1), self.room)

    def test_unknown_allocation_is_rejected(self):
        with self.assertRaisesMessage(services.AllocationError, "no longer exists"):
            services.deallocate_student(allocation_id=uuid.uuid4())

    def test_deallocate_button_flow(self):
        """REQ-9 through the Room Allocation page."""
        allocation = services.allocate_student(student_id=self.s1.pk, room_id=self.room.pk)
        self.client.force_login(self.admin)
        page = self.client.get(reverse("rooms:allocate"))
        url = reverse("rooms:deallocate", args=[allocation.pk])
        self.assertContains(page, f'action="{url}"')
        response = self.client.post(url, follow=True)
        self.assertRedirects(response, reverse("rooms:allocate"))
        self.assertContains(response, "was deallocated from room B1-101.")
        self.assertFalse(Allocation.objects.exists())

    def test_deallocate_twice_shows_error(self):
        allocation = services.allocate_student(student_id=self.s1.pk, room_id=self.room.pk)
        self.client.force_login(self.admin)
        url = reverse("rooms:deallocate", args=[allocation.pk])
        self.client.post(url)
        response = self.client.post(url, follow=True)
        self.assertContains(response, "This allocation no longer exists.")

    def test_deallocate_needs_post(self):
        allocation = services.allocate_student(student_id=self.s1.pk, room_id=self.room.pk)
        self.client.force_login(self.admin)
        response = self.client.get(reverse("rooms:deallocate", args=[allocation.pk]))
        self.assertEqual(response.status_code, 405)
        self.assertTrue(Allocation.objects.exists())

    def test_student_sees_no_room_after_deallocation(self):
        allocation = services.allocate_student(student_id=self.s1.pk, room_id=self.room.pk)
        services.deallocate_student(allocation_id=allocation.pk)
        self.client.force_login(self.s1)
        response = self.client.get(reverse("rooms:my_room"))
        self.assertContains(response, "No room allocated yet")
