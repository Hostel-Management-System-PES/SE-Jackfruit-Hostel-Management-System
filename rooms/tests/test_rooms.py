"""Tests for blocks, rooms, allocation and CSRF (REQ-6, REQ-7, REQ-8, REQ-10, SEC-5)."""
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from rooms import services
from rooms.models import Allocation, Block, Room

User = get_user_model()


def make_student(email, srn, verified=True):
    return User.objects.create_user(
        email=email,
        password="Pass@1234x",
        name=email.split("@")[0],
        srn=srn,
        registration_status=User.Status.VERIFIED if verified else User.Status.PENDING,
    )


class RoomSetupTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            email="admin@example.com", password="Admin@2026", name="Admin"
        )
        self.client.force_login(self.admin)
        self.block = Block.objects.create(name="B1")

    def test_admin_creates_block_and_room(self):
        """REQ-6: admin defines a block and a room with a capacity."""
        self.client.post(reverse("rooms:room_list"), {"action": "add_block", "name": "B2"})
        self.assertTrue(Block.objects.filter(name="B2").exists())
        response = self.client.post(
            reverse("rooms:room_list"),
            {"action": "add_room", "block": self.block.pk, "room_number": "101", "room_type": "Double", "capacity": 2},
            follow=True,
        )
        self.assertRedirects(response, reverse("rooms:room_list"))
        self.assertContains(response, "Room B1-101 was added successfully.")
        room = Room.objects.get(room_number="101")
        self.assertEqual(room.capacity, 2)
        self.assertEqual(room.status, Room.Status.VACANT)

    def test_invalid_capacity_is_rejected(self):
        """REQ-6: capacity must be at least 1."""
        response = self.client.post(
            reverse("rooms:room_list"),
            {"action": "add_room", "block": self.block.pk, "room_number": "102", "room_type": "Single", "capacity": 0},
        )
        self.assertContains(response, "Capacity must be at least 1")
        self.assertFalse(Room.objects.exists())

    def test_duplicate_room_number_in_block_is_rejected(self):
        Room.objects.create(block=self.block, room_number="101", room_type="Single", capacity=1)
        response = self.client.post(
            reverse("rooms:room_list"),
            {"action": "add_room", "block": self.block.pk, "room_number": "101", "room_type": "Single", "capacity": 1},
        )
        self.assertContains(response, "already exists")
        self.assertEqual(Room.objects.count(), 1)

    def test_room_list_shows_rooms(self):
        Room.objects.create(block=self.block, room_number="101", room_type="Double", capacity=2)
        response = self.client.get(reverse("rooms:room_list"))
        self.assertContains(response, "B1-101")
        self.assertContains(response, "0 / 2")

    def test_admin_dashboard_shows_room_card(self):
        Room.objects.create(block=self.block, room_number="101", room_type="Double", capacity=2)
        response = self.client.get(reverse("accounts:admin_dashboard"))
        self.assertContains(response, "Rooms vacant / total")
        self.assertContains(response, "1 / 1")


class AllocationTests(TestCase):
    def setUp(self):
        self.block = Block.objects.create(name="B1")
        self.room = Room.objects.create(
            block=self.block, room_number="101", room_type="Double", capacity=2
        )
        self.s1 = make_student("s1@example.com", "PES1UG24CS001")
        self.s2 = make_student("s2@example.com", "PES1UG24CS002")
        self.s3 = make_student("s3@example.com", "PES1UG24CS003")

    def test_allocate_available_room(self):
        """TC-ROOM-01: allocation saved, occupancy +1, student linked."""
        services.allocate_student(student_id=self.s1.pk, room_id=self.room.pk)
        self.assertEqual(self.room.occupied, 1)
        self.assertEqual(services.get_student_room(self.s1), self.room)
        self.room.refresh_from_db()
        self.assertEqual(self.room.status, Room.Status.VACANT)

    def test_room_becomes_occupied_when_full(self):
        """REQ-10: status changes to Occupied when occupancy reaches capacity."""
        services.allocate_student(student_id=self.s1.pk, room_id=self.room.pk)
        services.allocate_student(student_id=self.s2.pk, room_id=self.room.pk)
        self.room.refresh_from_db()
        self.assertEqual(self.room.status, Room.Status.OCCUPIED)

    def test_full_room_is_rejected(self):
        """TC-ROOM-02: allocating to a full room fails and occupancy stays the same."""
        services.allocate_student(student_id=self.s1.pk, room_id=self.room.pk)
        services.allocate_student(student_id=self.s2.pk, room_id=self.room.pk)
        with self.assertRaisesMessage(services.AllocationError, "is full"):
            services.allocate_student(student_id=self.s3.pk, room_id=self.room.pk)
        self.assertEqual(self.room.occupied, 2)

    def test_pending_student_is_rejected(self):
        """TC-ROOM-03: a Pending student cannot be allocated."""
        pending = make_student("p@example.com", "PES1UG24CS004", verified=False)
        with self.assertRaisesMessage(services.AllocationError, "verified"):
            services.allocate_student(student_id=pending.pk, room_id=self.room.pk)
        self.assertFalse(Allocation.objects.exists())

    def test_student_with_room_cannot_get_second_room(self):
        other = Room.objects.create(block=self.block, room_number="102", room_type="Single", capacity=1)
        services.allocate_student(student_id=self.s1.pk, room_id=self.room.pk)
        with self.assertRaisesMessage(services.AllocationError, "already has"):
            services.allocate_student(student_id=self.s1.pk, room_id=other.pk)

    def test_capacity_cannot_go_below_occupancy(self):
        services.allocate_student(student_id=self.s1.pk, room_id=self.room.pk)
        services.allocate_student(student_id=self.s2.pk, room_id=self.room.pk)
        admin = User.objects.create_superuser(email="a@example.com", password="Admin@2026", name="A")
        self.client.force_login(admin)
        response = self.client.post(
            reverse("rooms:room_edit", args=[self.room.pk]),
            {"block": self.block.pk, "room_number": "101", "room_type": "Single", "capacity": 1},
        )
        self.assertContains(response, "cannot be lower")

    def test_allocation_page_shows_error_for_full_room(self):
        admin = User.objects.create_superuser(email="a@example.com", password="Admin@2026", name="A")
        self.client.force_login(admin)
        services.allocate_student(student_id=self.s1.pk, room_id=self.room.pk)
        services.allocate_student(student_id=self.s2.pk, room_id=self.room.pk)
        response = self.client.post(
            reverse("rooms:allocate"), {"student": self.s3.pk, "room": self.room.pk}
        )
        self.assertContains(response, "is full (2 / 2). The student was not allocated.")
        self.assertContains(response, "Select a room that is not full.")
        self.assertEqual(Allocation.objects.count(), 2)

    def test_allocation_page_lists_only_eligible_students(self):
        """Student dropdown shows verified students without a room only."""
        admin = User.objects.create_superuser(email="a@example.com", password="Admin@2026", name="A")
        make_student("p@example.com", "PES1UG24CS009", verified=False)
        services.allocate_student(student_id=self.s1.pk, room_id=self.room.pk)
        self.client.force_login(admin)
        response = self.client.get(reverse("rooms:allocate"))
        self.assertNotContains(response, "PES1UG24CS009 - ")
        self.assertNotContains(response, "PES1UG24CS001 - ")
        self.assertContains(response, "PES1UG24CS002 - ")
        self.assertContains(response, "s1 (PES1UG24CS001)")


class RoomAccessTests(TestCase):
    def setUp(self):
        self.student = make_student("s1@example.com", "PES1UG24CS001")
        self.block = Block.objects.create(name="B1")
        self.room = Room.objects.create(block=self.block, room_number="101", room_type="Single", capacity=1)

    def test_student_cannot_open_admin_room_pages(self):
        self.client.force_login(self.student)
        self.assertEqual(self.client.get(reverse("rooms:room_list")).status_code, 403)
        self.assertEqual(self.client.get(reverse("rooms:allocate")).status_code, 403)

    def test_my_room_without_allocation(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse("rooms:my_room"))
        self.assertContains(response, "No room allocated yet")

    def test_my_room_shows_allocated_room(self):
        services.allocate_student(student_id=self.student.pk, room_id=self.room.pk)
        self.client.force_login(self.student)
        response = self.client.get(reverse("rooms:my_room"))
        self.assertContains(response, "B1-101")
        self.assertContains(response, "Occupied")

    def test_student_dashboard_shows_room_card(self):
        services.allocate_student(student_id=self.student.pk, room_id=self.room.pk)
        self.client.force_login(self.student)
        response = self.client.get(reverse("accounts:student_dashboard"))
        self.assertContains(response, "Allocated room")
        self.assertContains(response, "B1-101")

    def test_post_without_csrf_token_is_refused(self):
        """SEC-5: a state-changing POST without a CSRF token returns 403."""
        admin = User.objects.create_superuser(email="a@example.com", password="Admin@2026", name="A")
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(admin)
        response = csrf_client.post(
            reverse("rooms:allocate"), {"student": self.student.pk, "room": self.room.pk}
        )
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Allocation.objects.exists())
