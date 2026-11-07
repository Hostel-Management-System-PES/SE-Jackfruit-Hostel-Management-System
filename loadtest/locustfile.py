"""
Load test for NFR-1 / TC-PERF-01.

10 simulated users (8 students, 2 admins) open the standard pages:
dashboard, room list (availability), fee view. NFR-1 passes when the 95th
percentile response time is under 2000 ms.

Run (server must be running on port 8000, and seed.py run first):
    locust -f loadtest/locustfile.py --host http://127.0.0.1:8000 --headless -u 10 -r 2 -t 1m --csv loadtest/results
"""
import itertools
import re

from locust import HttpUser, between, task

PASSWORD = "Load@2026test"
CSRF_PATTERN = re.compile(r'name="csrfmiddlewaretoken" value="([^"]+)"')
_student_numbers = itertools.cycle(range(1, 11))


class LoggedInUser(HttpUser):
    abstract = True
    wait_time = between(1, 2)
    email = ""

    def on_start(self):
        page = self.client.get("/login/", name="login page")
        token = CSRF_PATTERN.search(page.text).group(1)
        response = self.client.post(
            "/login/",
            data={"username": self.email, "password": PASSWORD, "csrfmiddlewaretoken": token},
            headers={"Referer": f"{self.host}/login/"},
            name="login",
        )
        if "Logout" not in response.text:
            raise RuntimeError(f"Login failed for {self.email}. Did you run loadtest/seed.py?")


class StudentUser(LoggedInUser):
    weight = 4

    def on_start(self):
        self.email = f"loadstudent{next(_student_numbers)}@example.com"
        super().on_start()

    @task(3)
    def dashboard(self):
        self.client.get("/dashboard/", name="student dashboard")

    @task(2)
    def my_room(self):
        self.client.get("/rooms/my-room/", name="my room")

    @task(2)
    def my_fees(self):
        self.client.get("/fees/my/", name="fee details")


class AdminUser(LoggedInUser):
    weight = 1
    email = "loadadmin@example.com"

    @task(3)
    def room_list(self):
        self.client.get("/rooms/", name="room list (availability)")

    @task(2)
    def dashboard(self):
        self.client.get("/admin-panel/", name="admin dashboard")

    @task(1)
    def fee_overview(self):
        self.client.get("/fees/", name="fee overview")
