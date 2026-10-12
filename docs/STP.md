## 1. Introduction

- **Purpose:** This document defines the test plan for the Hostel Management System (HMS) v1.0: objectives, scope, strategy, environment, schedule and responsibilities.
- **Scope:** Testing covers registration with admin approval, login, role-based access, room allocation and deallocation, fee and payment recording, complaints, and leave requests with admin approval. Exclusions are listed in section 4.
- **References:** HMS SRS v1.3, HMS SAD v1.0, IEEE 829 (test documentation), OWASP ASVS.
- **Definitions:** HMS (Hostel Management System), SRS (Software Requirements Specification), SAD (Software Architecture and Design), RTM (Requirements Traceability Matrix), RBAC (Role-Based Access Control).

## 2. Test Items

- Accounts & Access module (registration, approval, login, roles, profile)
- Room Allocation module (blocks, rooms, allocation, deallocation, occupancy)
- Fee & Payment module (fee amount, payment records, outstanding balance, dues report)
- Complaints & Leave module (complaints, complaint status, leave requests, leave decisions)
- Role-based navigation and admin interface

## 3. Features to be Tested

Features are mapped to SRS requirement IDs.

### 3.1 Accounts & Access
- REQ-1: Student registration with unique email and SRN
- REQ-2: New accounts stay Pending until verified
- REQ-3: Admin approves or rejects a registration
- REQ-4: Role-based access to student and admin pages
- REQ-5: Student views and edits own profile
- REQ-21: Login with email or SRN and password
- SEC-1 to SEC-6: Password hashing, role-based access, input validation, session expiry, CSRF protection, audit log
<!-- STP-P2-1 -->
<!-- STP-P3-1 -->
<!-- STP-P4-2 -->

<!-- STP-P2-2 -->

<!-- STP-P2-3 -->

## 5.1 Security Validation

- Password handling (SEC-1): verify passwords are stored hashed and never appear in logs or error messages
- Access control (SEC-2): open admin URLs as a Student, and open Student A's records as Student B; expect 403
- Input validation (SEC-3): submit SQL fragments, script tags and over-long values in every form; expect rejection or safe escaping
- Session management (SEC-4): verify expired and tampered session cookies are rejected
- CSRF (SEC-5): submit a POST without a CSRF token; expect 403
- Audit log (SEC-6): perform a failed login and a room allocation; check the audit entries exist and contain no passwords or tokens
- Static analysis: SonarQube scan on every pull request; no open critical or high vulnerabilities at release
- Basic penetration test of the login and registration flow using OWASP ZAP or Postman before final submission

## 6. Test Environment

- **Hardware:** Developer laptops running Docker.
- **Software:** HMS application v1.0 (Django), PostgreSQL, latest Chrome and Firefox.
- **Tools:** pytest and Django test client (unit and integration), Postman (API), JMeter or Locust (performance), OWASP ZAP (security), SonarQube (static analysis), Jenkins (CI), GitHub Issues or Jira (defect tracking).
- **Test data:** Dummy students (Verified and Pending), one Admin, 10 rooms across 2 blocks and sample fee records, loaded from a fixture file.

<!-- STP-P3-2 -->

<!-- STP-P3-3 -->

<!-- STP-P3-4 -->

<!-- STP-P3-5 -->

<!-- STP-P2-4 -->

<!-- STP-P2-5 -->

<!-- STP-P4-3 -->

<!-- STP-P3-6 -->

<!-- STP-P4-4 -->

## 16. Test Cases

Each test case lists the requirement it verifies, its level (Unit, Integration or System), pre-conditions, steps, test data and the expected result. Actual Result and Pass/Fail are filled after execution on the implemented feature.

### 16.1 Accounts & Access

| Test Case ID | Requirement | Level | Description | Pre-conditions | Steps | Test Data | Expected Result | Actual Result | Pass/Fail |
|---|---|---|---|---|---|---|---|---|---|
| TC-ACC-01 | REQ-21 | System | Verified student logs in | Verified student account exists | 1) Open login page 2) Enter email and password 3) Submit | student1@example.com / Pass@1234 | Redirected to the student dashboard | | |
| TC-ACC-02 | REQ-21 | System (negative) | Wrong password is rejected | Verified student account exists | 1) Open login page 2) Enter valid email 3) Enter wrong password 4) Submit | student1@example.com / wrongpass | Login refused with an Invalid credentials message; no session is created | | |
| TC-ACC-03 | REQ-1 | System (negative) | Duplicate email or SRN is rejected | student1@example.com and SRN PES1UG24CS001 already registered | 1) Register with the same email and a new SRN 2) Register with a new email and the same SRN | student1@example.com / new SRN, then new email / PES1UG24CS001 | Both registration attempts are rejected with an already registered message; no duplicate user is created | | |
| TC-ACC-04 | REQ-2, REQ-3, REQ-21 | Integration | New account cannot log in until the Admin approves it | Admin account exists | 1) Register a new student 2) Try to log in 3) Admin approves the registration 4) Log in again | student9@example.com | Step 2 is refused because the account is Pending; step 4 succeeds and the account status is Verified | | |
| TC-SEC-01 | REQ-4, SEC-2 | System (security) | Student cannot open an admin page | Logged in as Student | 1) Request the admin rooms URL directly | Student session, actual admin URL | Access is denied with a 403 response or redirected to login; no admin data is exposed | | |

<!-- STP-P2-6 -->

<!-- STP-P3-7 -->

<!-- STP-P4-5 -->
