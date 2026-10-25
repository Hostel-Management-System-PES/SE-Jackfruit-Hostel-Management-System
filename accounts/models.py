"""
Custom user model for Students and Admins (TECH-01, REQ-1, REQ-2).

Both roles live in one table and are told apart by `role` (SRS 4.2).
Field layout follows SRS Appendix B (Student table).
"""
import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("An email address is required.")
        email = self.normalize_email(email).lower()
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # SEC-1: stores a salted hash, never plain text
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("role", User.Role.STUDENT)
        extra_fields.setdefault("registration_status", User.Status.PENDING)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """Admin accounts are created by developers (SRS 2.6), not by self-registration."""
        extra_fields.setdefault("role", User.Role.ADMIN)
        extra_fields.setdefault("registration_status", User.Status.VERIFIED)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        STUDENT = "Student", "Student"
        ADMIN = "Admin", "Admin"

    class Status(models.TextChoices):
        PENDING = "Pending", "Pending"
        VERIFIED = "Verified", "Verified"
        REJECTED = "Rejected", "Rejected"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    # srn and guardian_contact are mandatory only when role = Student (SRS Appendix B).
    srn = models.CharField("SRN", max_length=20, unique=True, null=True, blank=True)
    guardian_contact = models.CharField(max_length=15, blank=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.STUDENT)
    registration_status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    class Meta:
        ordering = ["name"]

    def __str__(self):
        if self.srn:
            return f"{self.name} ({self.srn})"
        return self.name

    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN

    @property
    def is_student_role(self):
        return self.role == self.Role.STUDENT

    @property
    def is_verified(self):
        return self.registration_status == self.Status.VERIFIED
