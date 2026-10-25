"""
Business rules of the Accounts module (REQ-1, REQ-2, REQ-3).

Other modules may call the read-only helpers at the bottom
(verified_students, students) but never change accounts data directly.
"""
from django.db import transaction

from .models import User


class AccountError(Exception):
    """A business rule of the Accounts module was broken."""


def register_student(*, name, email, srn, guardian_contact, password):
    """REQ-1, REQ-2: create a student account that stays Pending until verified."""
    return User.objects.create_user(
        email=email,
        password=password,
        name=name.strip(),
        srn=srn.strip().upper(),
        guardian_contact=guardian_contact.strip(),
        role=User.Role.STUDENT,
        registration_status=User.Status.PENDING,
    )


def decide_registration(*, user_id, decision):
    """REQ-3: an Admin approves (Verified) or rejects (Rejected) a Pending student."""
    if decision not in (User.Status.VERIFIED, User.Status.REJECTED):
        raise AccountError("Decision must be Verified or Rejected.")

    with transaction.atomic():
        try:
            user = User.objects.select_for_update().get(pk=user_id, role=User.Role.STUDENT)
        except User.DoesNotExist as exc:
            raise AccountError("Student registration not found.") from exc
        if user.registration_status != User.Status.PENDING:
            raise AccountError("This registration has already been decided.")
        user.registration_status = decision
        user.save(update_fields=["registration_status"])
    return user


def pending_students():
    return User.objects.filter(role=User.Role.STUDENT, registration_status=User.Status.PENDING)


def students():
    return User.objects.filter(role=User.Role.STUDENT)


def verified_students():
    return User.objects.filter(role=User.Role.STUDENT, registration_status=User.Status.VERIFIED)
