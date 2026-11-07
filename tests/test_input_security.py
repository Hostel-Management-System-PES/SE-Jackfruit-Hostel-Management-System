"""
SEC-3: user input is validated and made safe before it is used.

- HTML/JavaScript typed into a form is shown as text, never run (auto-escaping).
- SQL fragments are treated as plain text (the ORM uses parameterised queries).
- Input that is too long or in the wrong format is rejected with a message.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from complaints.models import Complaint
from fees.models import PaymentRecord
from rooms import services as room_services
from rooms.models import Block, Room

User = get_user_model()
SCRIPT = '<script>alert("x")</script>'
ESCAPED = "&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt;"
SQL = "' OR '1'='1'; DROP TABLE accounts_user; --"


class InputSecurityTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            email="admin@example.com", password="Admin@2026", name="Admin"
        )
        self.student = User.objects.create_user(
            email="asha@example.com",
            password="Pass@1234x",
            name="Asha",
            srn="PES1UG24CS001",
            guardian_contact="9876543210",
            registration_status=User.Status.VERIFIED,
        )
        self.room = Room.objects.create(
            block=Block.objects.create(name="B1"), room_number="101", room_type="Double", capacity=2
        )
        room_services.allocate_student(student_id=self.student.pk, room_id=self.room.pk)

    def register(self, **overrides):
        data = {
            "name": "Ravi",
            "email": "ravi@example.com",
            "srn": "PES1UG24CS002",
            "guardian_contact": "9876543210",
            "password1": "Strong@Pass2026",
            "password2": "Strong@Pass2026",
        }
        data.update(overrides)
        return self.client.post(reverse("accounts:register"), data)

    # ---- Script tags are escaped -------------------------------------------------

    def test_script_in_complaint_is_escaped_for_admin(self):
        self.client.force_login(self.student)
        self.client.post(reverse("complaints:student_page"), {"action": "complaint", "description": SCRIPT})
        self.assertEqual(Complaint.objects.get().description, SCRIPT)  # stored as typed
        self.client.force_login(self.admin)
        response = self.client.get(reverse("complaints:admin_page"))
        self.assertNotContains(response, SCRIPT)
        self.assertContains(response, ESCAPED)

    def test_script_in_registration_name_is_escaped_for_admin(self):
        self.register(name=SCRIPT)
        self.client.force_login(self.admin)
        response = self.client.get(reverse("accounts:admin_dashboard"))
        self.assertNotContains(response, SCRIPT)
        self.assertContains(response, ESCAPED)

    def test_script_in_leave_reason_is_escaped(self):
        self.client.force_login(self.student)
        self.client.post(
            reverse("complaints:student_page"),
            {"action": "leave", "start_date": "2026-12-01", "end_date": "2026-12-03", "reason": SCRIPT},
        )
        response = self.client.get(reverse("complaints:student_page"))
        self.assertNotContains(response, SCRIPT)
        self.assertContains(response, ESCAPED)

    # ---- SQL fragments are plain text ---------------------------------------------

    def test_sql_in_login_is_just_a_failed_login(self):
        response = self.client.post(reverse("accounts:login"), {"username": SQL, "password": SQL})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertEqual(User.objects.count(), 2)  # the user table is untouched

    def test_sql_in_complaint_is_stored_as_text(self):
        self.client.force_login(self.student)
        self.client.post(reverse("complaints:student_page"), {"action": "complaint", "description": SQL})
        self.assertEqual(Complaint.objects.get().description, SQL)
        self.assertEqual(User.objects.count(), 2)

    def test_sql_in_srn_is_rejected(self):
        response = self.register(srn="1'OR'1")
        self.assertContains(response, "SRN must be 6 to 20 letters or digits.")
        self.assertFalse(User.objects.filter(email="ravi@example.com").exists())

    # ---- Overlong and badly formatted input is rejected ------------------------------

    def test_overlong_complaint_is_rejected(self):
        self.client.force_login(self.student)
        self.client.post(reverse("complaints:student_page"), {"action": "complaint", "description": "x" * 1001})
        self.assertFalse(Complaint.objects.exists())

    def test_overlong_name_is_rejected(self):
        self.register(name="A" * 101)
        self.assertFalse(User.objects.filter(email="ravi@example.com").exists())

    def test_bad_phone_is_rejected(self):
        response = self.register(guardian_contact="98765<b>43210")
        self.assertContains(response, "Enter a valid phone number")
        self.assertFalse(User.objects.filter(email="ravi@example.com").exists())

    def test_text_in_payment_amount_is_rejected(self):
        self.client.force_login(self.admin)
        self.client.post(
            reverse("fees:overview"),
            {
                "action": "record_payment",
                "payment-student": self.student.pk,
                "payment-amount": "100; DROP TABLE fees_fee",
                "payment-payment_date": "2026-10-01",
            },
        )
        self.assertFalse(PaymentRecord.objects.exists())

    def test_overlong_room_number_is_rejected(self):
        self.client.force_login(self.admin)
        self.client.post(
            reverse("rooms:room_list"),
            {"action": "add_room", "block": self.room.block.pk, "room_number": "9" * 50, "room_type": "Single", "capacity": 1},
        )
        self.assertEqual(Room.objects.count(), 1)

    def test_post_without_csrf_token_is_refused(self):
        from django.test import Client

        client = Client(enforce_csrf_checks=True)
        client.force_login(self.student)
        response = client.post(reverse("complaints:student_page"), {"action": "complaint", "description": "Fan broken"})
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Complaint.objects.exists())
