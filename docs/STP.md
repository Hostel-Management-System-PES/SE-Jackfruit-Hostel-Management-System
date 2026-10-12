# Software Test Plan (STP) - Hostel Management System

**Project:** Hostel Management System (HMS)

**Version:** 1.0

**Authors:** Group G-03 - Tejasvi K S, Prathiksha B P, Vilohith, Varsha

**Date:** 12-10-2026

**Status:** Ready for review 1

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
### 3.2 Room Allocation
- REQ-6: Define blocks and rooms with a capacity
- REQ-7: Prevent allocation beyond capacity
- REQ-8: Allocate a room to a Verified student
- REQ-9: Deallocate a student from a room
- REQ-10: Automatic occupancy and status update
- NFR-1: Response time of standard pages under load

### 3.3 Fee & Payment
- REQ-11: Admin defines a fee amount for a student
- REQ-12: Admin records a payment
- REQ-13: Outstanding balance is fee minus total payments
- REQ-14: A payment cannot exceed the outstanding balance
- REQ-15: Student views own fee, payments and outstanding balance
- REQ-16: Admin views the outstanding dues report

### 3.4 Complaints & Leave
- REQ-17: Student files a complaint for their allocated room
- REQ-18: Admin updates complaint status
- REQ-19: Student submits a leave request with a valid date range
- REQ-20: Admin approves or rejects a pending leave request

### 3.5 Non-functional
- NFR-1 performance: response time of standard pages
- NFR-2 usability: number of screens to file a complaint
- NFR-3 to NFR-5: reliability, maintainability and browser compatibility (planned)
- Security: see section 5.1

## 4. Features Not to be Tested

- Django framework and PostgreSQL internals (assumed tested by their projects)
- Hosting, server and network infrastructure
- Online payment gateways, email and SMS delivery (out of scope in the SRS)
- Browsers other than the latest Chrome and Firefox
- Third-party libraries beyond their use in HMS

## 5. Test Approach / Strategy

**Levels**
- Unit tests: model and service functions with pytest (for example outstanding balance, capacity check)
- Integration tests: views, services and database together with the Django test client
- System tests: end-to-end flows through the browser (for example register, approve, allocate, file complaint)
- Acceptance tests: demo walkthrough of all use cases by the team and faculty

**Types**
- Functional testing of every REQ
- Negative and boundary testing (invalid input, full room, payment above outstanding)
- Regression testing: the automated suite runs on every pull request in Jenkins
- Performance testing against NFR-1 with JMeter or Locust
- Usability testing against NFR-2 (screen count)
- Security testing (see section 5.1)

**Entry criteria:** build passes CI, test data fixtures are loaded, the Docker environment runs, SRS v1.3 is the frozen baseline.

**Exit criteria:** all planned test cases are executed; no open critical or high defects; at least 70% line coverage per module (NFR-4); no critical SonarQube vulnerabilities; every requirement in the RTM has a test case or a planned one.

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

## 7. Test Schedule

| Milestone | Date |
|---|---|
| Test case design | 09-Oct-2026 to 10-Oct-2026 |
| Environment setup (Docker, fixtures) | 10-Oct-2026 |
| Test plan review | 11-Oct-2026 |
| Final edit and submission | 12-Oct-2026 |
| Unit and integration tests written and run with each feature | Every sprint of the implementation phase |
| System, security and performance tests, then test summary report | Before the final demo |


## 8. Test Deliverables

- Test Plan (this document)
- Test cases (section 16)
- Test scripts (pytest files, Postman collection, JMeter or Locust script)
- Test data (fixture files)
- Test execution logs and CI reports
- Coverage report
- Defect reports (GitHub Issues or Jira)
- Test Summary Report

## 9. Roles and Responsibilities

| Role | Name | Responsibility |
|---|---|---|
| Test Lead | Vilohith | Metrics, CI test runs, defect tracking, test summary report |
| Security Test Owner | Tejasvi K S | Security validation (section 5.1), SonarQube and OWASP ZAP runs, accounts tests |
| Integration and Performance Test Owner | Prathiksha B P | Test environment, room allocation tests, performance tests |
| STP Editor and Requirements Traceability | Varsha | Traceability matrix, complaints and leave tests, final document |
| Product Owner / Approver | Faculty | Reviews and approves the plan and results |

## 10. Risks and Mitigation

| Risk | Mitigation |
|---|---|
| Delay in a stable build | Small pull requests merged often, smoke tests on every CI run |
| Test environment differs between laptops | Single Docker setup shared by the whole team |
| Not enough time to execute all cases | Run High priority requirements first, automate unit and regression tests |
| Inconsistent test data | Fixture files kept in the repository and reloaded before each run |


## 11. Assumptions & Dependencies

- SRS v1.3 is the baseline and does not change during testing
- PostgreSQL and Docker are available on every team member's laptop
- Test data fixtures are created before test execution starts
- Jenkins and SonarQube are reachable during the implementation phase

## 12. Suspension & Resumption Criteria

**Suspend testing if:**
- The test environment is unavailable for more than 4 hours
- The build fails its smoke test, or blocks more than 30% of the planned test cases
- A critical defect in login blocks all other tests

**Resume testing when:**
- Blocking defects are fixed and the smoke test passes
- The environment is restored and the test data is reloaded

## 13. Test Case Management & Traceability

The Requirements Traceability Matrix (RTM) maps SRS requirements to test cases. Test cases are listed in section 16. Entries marked Planned receive further test cases in the implementation phase.

| Requirement | Test cases |
|---|---|
| REQ-1 | TC-ACC-03 |
| REQ-2 | TC-ACC-04 |
| REQ-3 | TC-ACC-04 |
| REQ-4 | TC-SEC-01 |
| REQ-5 | Planned |
| REQ-6 | Planned |
| REQ-7 | TC-ROOM-02 |
| REQ-8 | TC-ROOM-01, TC-ROOM-03 |
| REQ-9 | TC-ROOM-04 |
| REQ-10 | TC-ROOM-01, TC-ROOM-04 |
| REQ-11 | TC-FEE-01 |
| REQ-12 | TC-FEE-01 |
| REQ-13 | TC-FEE-01 |
| REQ-14 | TC-FEE-02 |
| REQ-15 | TC-FEE-03 |
| REQ-16 | Planned |
| REQ-17 | TC-REQ-01 |
| REQ-18 | TC-REQ-02 |
| REQ-19 | TC-REQ-03 |
| REQ-20 | TC-REQ-04 |
| REQ-21 | TC-ACC-01, TC-ACC-02, TC-ACC-04 |
| SEC-1 | Planned (section 5.1) |
| SEC-2 | TC-SEC-01 |
| SEC-3 | Planned (section 5.1) |
| SEC-4 | TC-SEC-02 |
| SEC-5 | Planned (section 5.1) |
| SEC-6 | Planned (section 5.1) |
| NFR-1 | TC-PERF-01 |
| NFR-2 | TC-USE-01 |
| NFR-3 | Planned |
| NFR-4 | Planned (coverage report) |
| NFR-5 | Planned |

## 14. Test Metrics & Reporting

**Metrics collected**
- % of test cases executed
- % passed and failed
- Requirement coverage (requirements with at least one executed test case)
- Defect density per module
- Line coverage per module

**Reports**
- Test execution status at the end of each sprint
- Final Test Summary Report before the demo


## 15. Approvals

| Role | Name | Signature / Date |
|---|---|---|
| Test Lead | Vilohith | |
| Dev Lead | Tejasvi K S | |
| Faculty | | |

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

### 16.2 Room Allocation

| Test Case ID | Requirement | Level | Description | Pre-conditions | Steps | Test Data | Expected Result | Actual Result | Pass/Fail |
|---|---|---|---|---|---|---|---|---|---|
| TC-ROOM-01 | REQ-8, REQ-10 | Integration | Allocate an available room to a Verified student | Verified student without a room; room with capacity 2 and 0 occupied | 1) Log in as Admin 2) Open allocation 3) Select student and room 4) Submit | Student S1, Room B1-101 | Allocation saved, occupancy becomes 1, S1 shows room B1-101 | | |
| TC-ROOM-02 | REQ-7 | Unit (boundary) | Allocation to a full room is rejected | Room with capacity 2 and 2 occupied | 1) Log in as Admin 2) Try to allocate another Verified student to the room | Student S3, Room B1-102 | Rejected with room is full message, occupancy stays 2 | | |
| TC-ROOM-03 | REQ-8 | Unit (negative) | A Pending student cannot be allocated a room | Student S4 with status Pending; room available | 1) Log in as Admin 2) Try to allocate S4 | Student S4, Room B1-103 | Rejected, no allocation created | | |
| TC-ROOM-04 | REQ-9, REQ-10 | Integration | Deallocate a student from a room | S1 allocated to B1-101 (occupied 1) | 1) Log in as Admin 2) Deallocate S1 | Student S1 | Allocation removed, occupancy becomes 0, room shows Vacant, S1 dashboard shows No room allocated yet | | |
| TC-PERF-01 | NFR-1 | Performance | Availability page response time under load | 50 rooms seeded | 1) Run JMeter or Locust with 10 concurrent users for 1 minute against the availability page | 10 users, 1 minute | 95% of responses within 2 seconds | | |

### 16.3 Fee & Payment

| Test Case ID | Requirement | Level | Description | Pre-conditions | Steps | Test Data | Expected Result | Actual Result | Pass/Fail |
|---|---|---|---|---|---|---|---|---|---|
| TC-FEE-01 | REQ-11, REQ-12, REQ-13 | Unit | Recording a payment reduces the outstanding balance | Student S1 with fee 50000 defined and nothing paid | 1) Log in as Admin 2) Record a payment 3) Open S1's dues | S1, amount 20000 | Payment saved, outstanding shows 30000 | | |
| TC-FEE-02 | REQ-14 | Unit (boundary) | A payment above the outstanding balance is rejected, the exact amount is accepted | S1 outstanding 30000 | 1) Record 30001 2) Record 30000 | 30001 then 30000 | First refused with a message and no record created; second accepted and outstanding becomes 0 | | |
| TC-FEE-03 | REQ-15 | System | Student sees only their own fee details | S1 and S2 have fees and payments; S1 logged in | 1) Open Fee Details 2) Change the URL to open S2's dues | S1, S2 | Own fee, payments and outstanding shown; S2's details refused with 403 | | |
| TC-SEC-02 | SEC-4 | System (security) | Expired session is rejected | S1 logged in, session then expired | 1) Expire the session (clear the server session or set a past expiry) 2) Open S1's dues page | S1 session | Redirected to login or 401, no dues data shown | | |

### 16.4 Complaints & Leave

| Test Case ID | Requirement | Level | Description | Pre-conditions | Steps | Test Data | Expected Result | Actual Result | Pass/Fail |
|---|---|---|---|---|---|---|---|---|---|
| TC-REQ-01 | REQ-17 | System | Student with an allocated room files a complaint | S1 logged in and allocated a room | 1) Open complaints 2) Enter description 3) Submit | Tap leaking | Complaint saved with status Open, linked to S1's room and shown under My complaints | | |
| TC-REQ-02 | REQ-18 | Integration | Admin updates complaint status | Open complaint from S1 | 1) Log in as Admin 2) Set status In-progress 3) Set status Resolved 4) Log in as S1 and open complaints | Complaint C1 | Status changes at each step and S1 sees Resolved | | |
| TC-REQ-03 | REQ-19 | Unit (negative) | Leave with end date before start date is rejected | Student S1 logged in | 1) Open leave form 2) Enter dates 3) Submit | from 20-Oct-2026, to 18-Oct-2026 | Rejected with validation message, no record created | | |
| TC-REQ-04 | REQ-20 | Integration | Admin approves a pending leave and cannot decide it twice | Pending leave request from S1 | 1) Log in as Admin 2) Approve the request 3) Try to reject the same request | Leave L1 | First step: status Approved and visible to S1; second step refused as already decided, status stays Approved | | |
| TC-USE-01 | NFR-2 | Usability | New student files a complaint in few screens | New student logged in and allocated a room | 1) Observer counts screens from the dashboard to the confirmation | New student account | Done in no more than 4 screens | | |
