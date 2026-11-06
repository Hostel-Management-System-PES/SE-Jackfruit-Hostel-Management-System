"""
Authorization matrix for every module (SEC-2, REQ-4, TC-SEC-01).

Every admin page must refuse students (403) and send anonymous users to the
login page, and every student page must refuse admins. Pages of modules that
are not installed yet are skipped, so this test keeps working as modules are
merged, and checks each new page automatically once it exists.
"""
import uuid

from django.test import TestCase
from django.urls import NoReverseMatch, reverse

from accounts.models import User

ANY_ID = uuid.uuid4()

# (url name, kwargs, HTTP method)
ADMIN_PAGES = [
    ("accounts:admin_dashboard", {}, "get"),
    ("accounts:decide_registration", {"user_id": ANY_ID}, "post"),
    ("rooms:room_list", {}, "get"),
    ("rooms:room_edit", {"pk": ANY_ID}, "get"),
    ("rooms:allocate", {}, "get"),
    ("rooms:deallocate", {"allocation_id": ANY_ID}, "post"),
    ("fees:overview", {}, "get"),
    ("fees:student_detail", {"student_id": ANY_ID}, "get"),
    ("fees:dues_report", {}, "get"),
    ("complaints:admin_page", {}, "get"),
    ("complaints:update_complaint_status", {"complaint_id": ANY_ID}, "post"),
    ("complaints:decide_leave", {"leave_id": ANY_ID}, "post"),
    ("audit:log_list", {}, "get"),
]

STUDENT_PAGES = [
    ("accounts:student_dashboard", {}, "get"),
    ("accounts:profile", {}, "get"),
    ("rooms:my_room", {}, "get"),
    ("fees:my_fees", {}, "get"),
    ("complaints:student_page", {}, "get"),
]

# Pages that exist since Sprint 1 and must always be found.
ALWAYS_PRESENT = {"accounts:admin_dashboard", "accounts:student_dashboard", "accounts:profile"}


def installed(pages):
    """Keep only the pages whose module is installed."""
    found = []
    for name, kwargs, method in pages:
        try:
            found.append((name, reverse(name, kwargs=kwargs), method))
        except NoReverseMatch:
            if name in ALWAYS_PRESENT:
                raise
    return found


class AuthorizationMatrixTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            email="admin@example.com", password="Admin@2026", name="Admin"
        )
        self.student = User.objects.create_user(
            email="s1@example.com",
            password="Pass@1234x",
            name="Student One",
            srn="PES1UG24CS001",
            registration_status=User.Status.VERIFIED,
        )
        self.pending = User.objects.create_user(
            email="p@example.com", password="Pass@1234x", name="Pending", srn="PES1UG24CS002"
        )

    def request(self, url, method):
        return getattr(self.client, method)(url)

    def test_student_gets_403_on_every_admin_page(self):
        self.client.force_login(self.student)
        for name, url, method in installed(ADMIN_PAGES):
            with self.subTest(page=name):
                self.assertEqual(self.request(url, method).status_code, 403)

    def test_admin_gets_403_on_every_student_page(self):
        self.client.force_login(self.admin)
        for name, url, method in installed(STUDENT_PAGES):
            with self.subTest(page=name):
                self.assertEqual(self.request(url, method).status_code, 403)

    def test_anonymous_user_is_sent_to_login_everywhere(self):
        login = reverse("accounts:login")
        for name, url, method in installed(ADMIN_PAGES + STUDENT_PAGES):
            with self.subTest(page=name):
                response = self.request(url, method)
                self.assertEqual(response.status_code, 302)
                self.assertTrue(response["Location"].startswith(login))

    def test_unverified_student_gets_403_on_student_pages(self):
        """A Pending account cannot use the system even with a session."""
        self.client.force_login(self.pending)
        for name, url, method in installed(STUDENT_PAGES):
            with self.subTest(page=name):
                self.assertEqual(self.request(url, method).status_code, 403)

    def test_student_cannot_open_another_students_records_by_url(self):
        """Object-level check: changing the id in the URL does not expose other records."""
        other = User.objects.create_user(
            email="s2@example.com",
            password="Pass@1234x",
            name="Student Two",
            srn="PES1UG24CS003",
            registration_status=User.Status.VERIFIED,
        )
        self.client.force_login(self.student)
        try:
            url = reverse("fees:student_detail", kwargs={"student_id": other.pk})
        except NoReverseMatch:
            self.skipTest("Fees module not installed")
        self.assertEqual(self.client.get(url).status_code, 403)

    def test_403_page_is_shown(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse("accounts:admin_dashboard"))
        self.assertContains(response, "Access denied", status_code=403)
