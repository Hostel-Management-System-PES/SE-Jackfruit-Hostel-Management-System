# Hostel Management System (HMS)

A web application for managing student details, hostel room allocation, fee records, complaints and leave requests for a single hostel. Built for the Software Engineering mini-project (UE24CS341A, PES University) using Agile/Scrum.

Documents: [SRS](docs/SRS.md) · [SAD](docs/SAD.md) · [Test Plan](docs/STP.md)

## Team and modules

| Member | Module | Folder |
|---|---|---|
| Vilohith (P1) | Accounts & Access: registration, admin approval, login, roles | `accounts/` |
| Prathiksha (P2) | Room & Allocation: blocks, rooms, capacity, allocation | `rooms/` |
| Tejasvi (P3) | Fee Management: fees, payments, outstanding balance | `fees/` |
| Varsha (P4) | Complaints & Leave: complaints, leave requests | `complaints/` |

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

## Run the tests

```bash
pytest
```

GitHub Actions runs the same tests against PostgreSQL on every push and pull request (`.github/workflows/ci.yml`).

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
rooms/        P2: blocks, rooms, allocation
fees/         P3: fees, payments, outstanding balance
complaints/   P4: complaints, leave requests
templates/    shared layout (base.html, 403.html, form include)
static/       CSS
docs/         SRS, SAD, Test Plan, diagrams
```

Each module has the same layout: `models.py` (tables), `services.py` (business rules), `forms.py` (input validation), `views.py` and `urls.py` (pages), `templates/`, and `tests/`.

Modules are independent: `hms/settings.py` enables `rooms`, `fees` and `complaints` automatically when their folder exists, and each module adds its own menu entries through `hms_menu` in its `apps.py`.

## Git workflow

1. `git checkout main && git pull`
2. `git checkout -b feature/<your-module>`
3. Commit small steps, then `git push -u origin feature/<your-module>`
4. Open a pull request into `main` with `Closes #<issue>` for each story it completes. CI must pass and one teammate reviews before merging.
