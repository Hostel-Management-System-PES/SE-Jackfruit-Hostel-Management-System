"""Tests for My Profile (REQ-5)."""
from django.test import TestCase
from django.urls import reverse

from accounts.models import User


def make_student(email="s1@example.com", srn="PES1UG24CS001", name="Asha Rao"):
    return User.objects.create_user(
        email=email,
        password="Pass@1234x",
        name=name,
        srn=srn,
        guardian_contact="9876543210",
        registration_status=User.Status.VERIFIED,
    )


class ProfileTests(TestCase):
    def setUp(self):
        self.student = make_student()
        self.url = reverse("accounts:profile")

    def test_student_sees_own_profile(self):
        """REQ-5: the profile shows the student's own details."""
        self.client.force_login(self.student)
        response = self.client.get(self.url)
        self.assertContains(response, "PES1UG24CS001")
        self.assertContains(response, "s1@example.com")
        self.assertContains(response, 'value="9876543210"')

    def test_student_updates_name_and_guardian_contact(self):
        """REQ-5: permitted fields are saved."""
        self.client.force_login(self.student)
        response = self.client.post(
            self.url, {"name": "Asha R. Rao", "guardian_contact": "9123456780"}, follow=True
        )
        self.assertRedirects(response, self.url)
        self.assertContains(response, "Your profile was updated.")
        self.student.refresh_from_db()
        self.assertEqual(self.student.name, "Asha R. Rao")
        self.assertEqual(self.student.guardian_contact, "9123456780")

    def test_invalid_update_is_rejected(self):
        """REQ-5: invalid values show an error and change nothing."""
        self.client.force_login(self.student)
        response = self.client.post(self.url, {"name": "   ", "guardian_contact": "abc"})
        self.assertContains(response, "Name is required.")
        self.assertContains(response, "valid phone number")
        self.student.refresh_from_db()
        self.assertEqual(self.student.name, "Asha Rao")

    def test_srn_and_email_cannot_be_changed(self):
        """Extra fields in the request are ignored: SRN and email stay the same."""
        self.client.force_login(self.student)
        self.client.post(
            self.url,
            {
                "name": "Asha Rao",
                "guardian_contact": "9876543210",
                "srn": "HACKED1234",
                "email": "hacker@example.com",
                "role": "Admin",
            },
        )
        self.student.refresh_from_db()
        self.assertEqual(self.student.srn, "PES1UG24CS001")
        self.assertEqual(self.student.email, "s1@example.com")
        self.assertEqual(self.student.role, User.Role.STUDENT)

    def test_student_cannot_edit_another_profile(self):
        """REQ-5: the page always edits the logged-in student, never someone else."""
        other = make_student("s2@example.com", "PES1UG24CS002", "Ravi Kumar")
        self.client.force_login(self.student)
        self.client.post(self.url, {"name": "Changed", "guardian_contact": "9123456780"})
        other.refresh_from_db()
        self.assertEqual(other.name, "Ravi Kumar")

    def test_dashboard_links_to_profile(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse("accounts:student_dashboard"))
        self.assertContains(response, f'href="{self.url}"')
        self.assertContains(response, "My Profile")

    def test_admin_and_anonymous_cannot_open_profile(self):
        admin = User.objects.create_superuser(email="a@example.com", password="Admin@2026", name="A")
        self.client.force_login(admin)
        self.assertEqual(self.client.get(self.url).status_code, 403)
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={self.url}")
