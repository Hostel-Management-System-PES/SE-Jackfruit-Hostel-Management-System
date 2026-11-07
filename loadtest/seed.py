"""
Creates the test data for the load test (TC-PERF-01): 50 rooms in 5 blocks,
one load-test admin and 10 verified students with fees.

Run from the project folder (with the virtual environment active):
    python loadtest/seed.py
Running it again is safe: existing records are kept.
"""
import os
import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hms.settings")

import django  # noqa: E402

django.setup()

from django.contrib.auth import get_user_model  # noqa: E402

from fees.models import Fee  # noqa: E402
from rooms.models import Block, Room  # noqa: E402

User = get_user_model()
ADMIN_EMAIL = "loadadmin@example.com"
STUDENT_EMAIL = "loadstudent{n}@example.com"
PASSWORD = "Load@2026test"


def main():
    if not User.objects.filter(email=ADMIN_EMAIL).exists():
        User.objects.create_superuser(email=ADMIN_EMAIL, password=PASSWORD, name="Load Test Admin")
    for b in range(1, 6):
        block, _ = Block.objects.get_or_create(name=f"L{b}")
        for r in range(1, 11):
            Room.objects.get_or_create(
                block=block,
                room_number=f"{b}{r:02d}",
                defaults={"room_type": "Double", "capacity": 2},
            )
    for n in range(1, 11):
        email = STUDENT_EMAIL.format(n=n)
        student = User.objects.filter(email=email).first()
        if student is None:
            student = User.objects.create_user(
                email=email,
                password=PASSWORD,
                name=f"Load Student {n}",
                srn=f"PES1UG24LT{n:03d}",
                guardian_contact="9876543210",
                registration_status=User.Status.VERIFIED,
            )
        Fee.objects.get_or_create(student=student, defaults={"amount": Decimal("60000")})
    print(f"Seeded {Room.objects.filter(block__name__startswith='L').count()} rooms, 1 admin, 10 students.")


if __name__ == "__main__":
    main()
