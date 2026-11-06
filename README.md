# Hostel Management System (HMS)

A web application for managing student details, hostel room allocation, fee records, complaints and leave requests for a single hostel. Built for the Software Engineering mini-project (UE24CS341A, PES University) using Agile/Scrum.

Documents: [SRS](docs/SRS.md) · [SAD](docs/SAD.md) · [Test Plan](docs/STP.md)

## Team and modules

| Member | Module | Folder |
|---|---|---|
| Vilohith (P1) | Accounts & Access: registration, admin approval, login, roles, student profile | `accounts/` |
| Prathiksha (P2) | Room & Allocation: blocks, rooms, allocation, deallocation; audit log; load test | `rooms/`, `audit/`, `loadtest/` |
| Tejasvi (P3) | Fee Management: fees, payments, Fee Details, dues report; coverage in CI | `fees/`, `.coveragerc` |
| Varsha (P4) | Complaints & Leave: complaints, leave requests, status updates, leave decisions; session security | `complaints/`, `security/` |

Roles: **Student** and **Admin**.

## Tech stack

Python 3.12 · Django 5.2 · PostgreSQL 16 (SQLite for quick local runs) · Docker · pytest · GitHub Actions · SonarQube Cloud

## Run locally (without Docker)

Without database settings, the app uses a local SQLite file, so you only need Python.

```bash
python -m venv .venv
# Windows:      .venv\Scripts\activate
# macOS/Linux:  source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser   # creates the Admin account (email, name, password)
python manage.py runserver
```

Open http://127.0.0.1:8000 and log in with the admin email and password.

Admin accounts are only created with `createsuperuser` (SRS 2.6). Students register at `/register/` and stay Pending until the admin approves them on the admin dashboard.

## Run with Docker (PostgreSQL)

```bash
docker compose up --build
docker compose exec web python manage.py createsuperuser
```

Open http://localhost:8000. Stop with `Ctrl+C`, or `docker compose down`.

## Features

**Student:** register, log in with email or SRN, dashboard, My Room, Fee Details (fee, payments, outstanding), Complaints & Leave, My Profile (edit name and guardian contact).

**Admin:** approve or reject registrations, Rooms & Blocks, Room Allocation (allocate and deallocate), Fees (set fee, record payment), Dues Report, Complaints & Leave (update complaint status, approve or reject leave), Audit Log.

## Run the tests

```bash
pytest
```

With the coverage report (NFR-4: at least 70% per module):

```bash
coverage run -m pytest
coverage report
coverage html        # then open htmlcov/index.html
```

GitHub Actions runs the same tests against PostgreSQL on every push and pull request (`.github/workflows/ci.yml`), fails if any module is below 70% coverage, and uploads the HTML coverage report as the `coverage-report` artifact of the run.

Test files by requirement:

| What | File |
|---|---|
| Role checks on every page (SEC-2) | `accounts/tests/test_authorization.py` |
| Input validation and escaping (SEC-3) | `tests/test_input_security.py` |
| Rollback of failed updates (NFR-3) | `tests/test_reliability.py` |
| Session expiry and logout (SEC-4) | `security/tests/test_sessions.py` |
| Audit log (SEC-6) | `audit/tests/test_audit.py` |
| Complaint in 4 screens (NFR-2) | `complaints/tests/test_usability.py` |

## Load test (NFR-1)

Checks that 95% of page requests finish within 2 seconds with 10 users. Needs a second terminal.

```bash
pip install -r loadtest/requirements.txt
python manage.py migrate
python loadtest/seed.py              # 50 rooms, 1 admin, 10 students
python manage.py runserver           # terminal 1
locust -f loadtest/locustfile.py --host http://127.0.0.1:8000 --headless -u 10 -r 2 -t 1m --csv loadtest/results   # terminal 2
```

Results are written to `docs/testing/performance_results.md`.

## Audit log and session security

- Every login, failed login, logout, denied page (403) and admin change (registration decision, room, allocation, fee, payment, complaint status, leave decision) is written to the audit log. Admins see it under **Audit Log**. Passwords are never logged. (SEC-6)
- A session ends after 30 minutes without activity, when the browser closes, or on logout. Old or forged session cookies are refused. (SEC-4)

## Static analysis (SonarQube Cloud)

`.github/workflows/sonar.yml` scans the code on every push and pull request. One-time setup (repository must be public for the free plan):

1. Sign in at https://sonarcloud.io with GitHub and import this repository.
2. In the SonarCloud project, turn off *Automatic Analysis* (Administration > Analysis Method).
3. Create a token (My Account > Security) and add it to GitHub: Settings > Secrets and variables > Actions > New secret named `SONAR_TOKEN`.
4. Check that `sonar.projectKey` and `sonar.organization` in `sonar-project.properties` match the SonarCloud project.

Until `SONAR_TOKEN` exists, the scan step is skipped.

## Project structure

```
hms/          project settings, URLs, navigation menu
accounts/     P1: user model, registration, login, role checks
rooms/        P2: blocks, rooms, allocation, deallocation
audit/        P2: audit log (signals + middleware)
loadtest/     P2: Locust load test and seed data
fees/         P3: fees, payments, Fee Details, dues report
complaints/   P4: complaints, leave requests, admin decisions
security/     P4: session settings (no pages)
tests/        P3: cross-module tests (input security, reliability)
templates/    shared layout (base.html, 403.html, form include)
static/       CSS
docs/         SRS, SAD, Test Plan, diagrams, testing results
```

Each module has the same layout: `models.py` (tables), `services.py` (business rules), `forms.py` (input validation), `views.py` and `urls.py` (pages), `templates/`, and `tests/`.

Modules are independent: `hms/settings.py` enables `rooms`, `fees`, `complaints`, `audit` and `security` automatically when their folder exists. Each module adds its own menu entries through `hms_menu` and dashboard cards through `hms_dashboard_cards` in its `apps.py`, and its own settings or middleware through an optional `hms_settings.py`.

## Git workflow

1. Each member works on their own branch. At the start of a sprint the branch is reset to `main`: `git fetch origin` then `git reset --hard origin/main`.
2. Commit one story at a time, with the story ID in the message.
3. Push the branch and open a pull request into `main` with `Closes #<issue>` for each story it completes.
4. CI must pass and one teammate reviews before merging. Never push to `main` directly.
