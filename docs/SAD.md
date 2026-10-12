# 3. Architecture

<!-- SAD-P1-1 -->

<!-- SAD-P3-1 -->

## 3.2 Stakeholders & Concerns

| Stakeholder | Concerns |
|---|---|
| Student | Easy view of room and fees, privacy of personal data, quick complaint and leave handling |
| Admin | Control over students, rooms, fees and requests; accurate records; dues report |
| Developers / maintainers | Modularity, readable code, testability |
| Faculty / evaluators | Traceability, security, evidence of process |

## 3.3 Component (UML) Diagram

![HMS component diagram](diagrams/component_diagram.png)

*Figure 1: HMS component diagram. Arrows show the direction of dependency.*

## 3.4 Component Descriptions

- **C1 Web UI (Templates):** server-rendered Django pages for Student and Admin; collects input and shows results.
- **C2 Accounts & Access:** registration with admin verification, login, sessions, roles and student profiles; used by every other component for authentication and authorisation.
- **C3 Room Allocation:** blocks, rooms with capacity, allocation, deallocation and occupancy status; asks C2 whether a student is Verified before allocating.
- **C4 Fee & Payment:** fee amount per student, payment records, outstanding balance and the dues report.
- **C5 Complaints & Leave:** complaint filing and status tracking, leave requests and Admin decisions; links records to the student (C2) and room (C3).
- **C6 PostgreSQL database:** stores users, rooms, fees, payments, complaints and leave requests with foreign-key constraints.
- **C7 Logging & Audit:** records failed logins, denied access and key business actions (allocation, payment, decisions) as required by SEC-6.

## 3.5 Chosen Architecture Pattern and Rationale

HMS uses a **layered modular monolith** built on Django's Model-View-Template style. Layers: Presentation (templates) -> Views (request handling and validation) -> Services (business rules) -> Models/ORM -> PostgreSQL. Each functional module is one Django app with its own models, views, services and tests, so team members work in separate folders and modules call each other only through service functions.

**Rejected alternatives:** microservices, because they add deployment and network complexity and make transactions such as allocation with an occupancy update harder, which is not justified for a four-person team and a single relational database; a flat single-app monolith, because it gives poor separation of concerns and constant merge conflicts.
<!-- SAD-P3-2 -->

### 3.8 Requirements Traceability

The following matrix maps the system requirements to their responsible architecture components and design sections. Requirement identifiers and descriptions follow Appendix C of the SRS. Code references and system test identifiers will be finalized when implementation and system testing are available.

| Req ID | Brief Description | Architecture Ref | Design Ref |
|---|---|---|---|
| REQ-1 | Student registration | Accounts Module | Section 4.3.1 |
| REQ-2 | Student login | Accounts Module | Section 4.3.1 |
| REQ-3 | Student profile management | Accounts Module | Section 4.3.1 |
| REQ-4 | Admin verifies student registration | Accounts Module | Section 4.3.1 |
| REQ-5 | Manage hostel blocks | Room Allocation Module | Section 4.3.2 |
| REQ-6 | Manage rooms | Room Allocation Module | Section 4.3.2 |
| REQ-7 | Allocate room | Room Allocation Module | Section 4.3.2 |
| REQ-8 | Deallocate room | Room Allocation Module | Section 4.3.2 |
| REQ-9 | View fee details | Fees Module | Section 4.3.3 |
| REQ-10 | Record fee payment | Fees Module | Section 4.3.3 |
| REQ-11 | View dashboard | Presentation Layer | Sections 4.1 and 4.5 |
| REQ-12 | View room availability | Room Allocation Module | Section 4.3.2 |
| REQ-13 | Manage hostel information | Admin and Hostel Management Components | Sections 3.4 and 4.3 |
| REQ-14 | Manage student records | Accounts Module | Section 4.3.1 |
| REQ-15 | View payment history | Fees Module | Section 4.3.3 |
| REQ-16 | View reports | Reporting and Admin Components | Sections 3.4 and 4.3 |
| REQ-17 | Student files a complaint linked to allocated room | Complaints and Leave Module | Section 4.3.4 |
| REQ-18 | Admin updates complaint status | Complaints and Leave Module | Section 4.3.4 |
| REQ-19 | Student submits leave request with valid dates and reason | Complaints and Leave Module | Sections 4.2.4 and 4.3.4 |
| REQ-20 | Admin approves or rejects pending leave request | Complaints and Leave Module | Sections 4.2.4 and 4.3.4 |
| REQ-21 | User login | Accounts Module | Section 4.3.1 |
| SEC-1 | Authentication and access control | Accounts and Security Components | Sections 3.4 and 3.9 |
| SEC-2 | Role-based authorization | Accounts and Security Components | Sections 3.4 and 3.9 |
| SEC-3 | Input validation | Application and Service Layers | Section 4.4 |
| SEC-4 | Session invalidation after logout or expiry | Accounts and Security Components | Sections 3.9 and 4.4 |
| SEC-5 | CSRF protection for state-changing submissions | Security Middleware | Sections 3.9 and 4.3 |
| SEC-6 | Audit logging of privileged actions and failed logins | Audit Logging Component | Sections 3.9 and 4.4 |
| NFR-1 | 95% of standard requests within 2 seconds with up to 10 concurrent users | Application and Database Layers | Section 4.4 |
| NFR-2 | Complaint filing in no more than 4 screens | Presentation Layer | Section 4.5 |
| NFR-3 | Reliability and transactional updates | Service and Database Layers | Section 4.4 |
| NFR-4 | Modular Django apps and at least 70% unit-test line coverage per module | Django Application Modules | Sections 3.4 and 4.1 |
| NFR-5 | Compatibility with latest Chrome and Firefox versions | Presentation Layer | Section 4.5 |

<!-- SAD-P1-3 -->

# 4. Design

### 4.1 Design Overview

The Jackfruit Hostel Management System follows a modular, layered design using Django and PostgreSQL. The presentation layer provides role-specific pages for Students and Admins. The application layer processes requests and enforces business rules, while the data layer stores and retrieves hostel information.

The system is divided into the following functional modules:

- **Accounts Module:** Handles user authentication, sessions, and role-based access for Students and Admins.
- **Room Allocation Module:** Manages hostel blocks, rooms, room availability, and student room allocation.
- **Fees Module:** Manages hostel fee information, payment records, and balance updates.
- **Complaints and Leave Module:** Allows Students to submit room-related complaints and leave requests. Admins can update complaint statuses and approve or reject pending leave requests.
- **Audit and Logging:** Records relevant security-sensitive actions and application errors for accountability and troubleshooting.

Each module uses Django models to represent its data, views to handle incoming requests, URL configurations to map routes, and templates to render pages. Business rules should be implemented in reusable service functions wherever appropriate, rather than duplicated across views.

PostgreSQL acts as the central database. Django's ORM provides database access, while validation and transaction handling help preserve data consistency. Authentication and role-based authorization restrict sensitive operations to permitted users.

For the Complaints and Leave Module, a Student must have an allocated room before submitting a room-related complaint. Leave requests must contain a valid date range and reason. Only an Admin can approve or reject a pending leave request. Once a request has been decided, the system must prevent a second decision from changing its status.

These modules interact through Django URL routes, views, service functions, and the shared database. This modular design supports maintainability, testing, and future extension.

## 4.2 UML Sequence Diagrams

### 4.2.1 Login and Role Check

The sequence diagram below illustrates authentication, account verification, session creation, role checking, and audit logging.

![Login and role check sequence](diagrams/seq_login.png)

### 4.2.2 Allocate a room (Room Allocation)
Shows the Admin allocating a room (REQ-7, REQ-8, REQ-10). The service rejects a student who is not Verified or already has a room, and a room that is full. The allocation and the occupancy change are saved in one database transaction (NFR-3) and the action is written to the audit log (SEC-6).

![Allocate room sequence](diagrams/seq_allocate_room.png)
<!-- SAD-P3-3 -->

### 4.2.4 Leave Approval Sequence Diagram

The sequence diagram describes how a Student submits a leave request and how an Admin approves or rejects it. The system validates the date range before saving the request with Pending status. An Admin can decide only a request that is still Pending. The decision is saved in the database and recorded for accountability.

**Diagram source:** `docs/diagrams/seq_leave_approval.puml`

**Diagram image:** `docs/diagrams/seq_leave_approval.png`

![Leave Approval Sequence Diagram](https://raw.githubusercontent.com/TejasviKS/SE-Jackfruit-Hostel-Management-System/docs/sad-p4/docs/diagrams/seq_leave_approval.png)

**Sequence flow:**

1. The Student submits a leave request with a start date, end date, and reason.
2. The system validates the dates. If the end date is earlier than the start date, it returns a validation error.
3. If the dates are valid, the system saves the request with Pending status.
4. The Admin views pending requests and selects Approve or Reject.
5. The system checks that the request is still Pending before updating its status.
6. The system records the Admin's decision in the audit log and displays the updated status.
7. If the request has already been decided, the system rejects the repeated decision.

This flow supports REQ-19 and REQ-20.

## 4.3 API Design

Interfaces below are Django URL routes that receive HTML form submissions (GET and POST). Request and response fields describe the form inputs and the page results. There is no separate REST API (SRS 3.3).

### 4.3.1 Accounts & Access API

**POST /accounts/register/** (REQ-1, REQ-2)
- Auth: none
- Request: {name, email, srn, guardian_contact, password}
- Response: {status, user_id} (account created as Pending)
- Errors: 400 missing or invalid field, 409 email or SRN already registered

**POST /accounts/login/** (REQ-21)
- Auth: none
- Request: {identifier (email or SRN), password}
- Response: {status, role, redirect}
- Errors: 401 invalid credentials or account not Verified

**POST /accounts/registrations/{id}/decision/** (REQ-3)
- Auth: Admin
- Request: {decision (Verified or Rejected)}
- Response: {user_id, registration_status}
- Errors: 400 invalid decision, 403 role not permitted, 404 registration not found

### 4.3.2 Room Allocation API

**GET /rooms/available/**
- Auth: logged-in user (Student or Admin)
- Request: query parameters block, room_type
- Response: list of {room_id, block, room_type, capacity, occupied}
- Errors: 400 invalid filter, 401 not logged in

**POST /rooms/allocate/** (REQ-7, REQ-8, REQ-10)
- Auth: Admin
- Request: {student_id, room_id}
- Response: {status, room_id, occupied}
- Errors: 400 invalid input, 403 role not permitted, 404 student or room not found, 409 room full, student not Verified, or student already allocated

**POST /rooms/deallocate/** (REQ-9, REQ-10)
- Auth: Admin
- Request: {student_id}
- Response: {status, room_id, occupied}
- Errors: 400 invalid input, 403 role not permitted, 404 student not found or has no room
<!-- SAD-P3-4 -->

### 4.3.4 Complaints and Leave API Design

The Complaints and Leave Module uses Django URL routes to handle student submissions and administrative decisions. The routes below describe the expected interfaces and must be aligned with the implemented Django URL configuration.

#### 4.3.4.1 Submit Complaint

- **Method and route:** `POST /complaints/`
- **Authorized role:** Student
- **Purpose:** Submit a complaint associated with the Student's allocated room.
- **Request fields:** `description` — a description of the issue.
- **Processing:** Validate the description and identify the Student's allocated room from the authenticated account.
- **Successful response:** Display a confirmation and the complaint status.
- **Error handling:** Reject missing or invalid descriptions. Deny unauthenticated users and Students without an allocated room.

#### 4.3.4.2 Update Complaint Status

- **Method and route:** `POST /complaints/{id}/status/`
- **Authorized role:** Admin
- **Purpose:** Change the status of an existing complaint.
- **Request fields:** `status` — an allowed status such as `In-progress` or `Resolved`.
- **Processing:** Verify the Admin's authorization, validate the requested status, and update the complaint.
- **Successful response:** Display the complaint's updated status.
- **Error handling:** Reject invalid statuses, deny unauthorized users, and report when the complaint does not exist.

#### 4.3.4.3 Submit Leave Request

- **Method and route:** `POST /leaves/`
- **Authorized role:** Student
- **Purpose:** Submit a request for leave or outing.
- **Request fields:** `start_date`, `end_date`, and `reason`.
- **Processing:** Validate the required fields and ensure that the end date is not earlier than the start date. Save a valid request with `Pending` status.
- **Successful response:** Display confirmation and the request status.
- **Error handling:** Reject missing fields or invalid date ranges and deny unauthenticated users.

#### 4.3.4.4 Approve or Reject Leave Request

- **Method and route:** `POST /leaves/{id}/decision/`
- **Authorized role:** Admin
- **Purpose:** Approve or reject a pending leave request.
- **Request fields:** `decision` — `Approved` or `Rejected`.
- **Processing:** Verify Admin authorization, validate the decision, and ensure the request is still `Pending` before updating it. Record the decision for accountability.
- **Successful response:** Display the updated leave status.
- **Error handling:** Reject invalid decisions, deny unauthorized users, report missing requests, and prevent a second decision from changing an already-decided request.

**Security:** All routes must enforce authentication and role-based authorization. User input must be validated on the server, and state-changing requests must be protected against CSRF. Error responses must not expose sensitive information.

**Requirement mapping:** REQ-17 and REQ-18 cover complaint handling; REQ-19 and REQ-20 cover leave submission and decisions. Verify the route names against the actual implementation before final submission.

<!-- SAD-P3-5 -->

### 4.5 User Experience Design

The system provides separate interfaces for Students and Admins. Navigation options and available actions depend on the authenticated user's role.

- **Student interface:** Provides access to the dashboard, allocated room information, fee details, complaint submission, and leave requests.
- **Admin interface:** Provides access to room allocation, fee and payment management, complaint status updates, and leave request decisions.
- **Form validation:** Forms display clear validation messages when required fields are missing or invalid. Failed submissions must not create unintended database changes.
- **Consistency:** Pages use consistent labels, navigation, and status indicators so that users can understand the current state of a request.
- **Accessibility and usability:** Pages should use readable text, clear labels, and understandable feedback messages.
- **Complaint workflow:** A Student should be able to submit a complaint within the maximum four-screen limit specified by NFR-2.

The following UI mockups provide visual references for the Student and Admin complaints and leave interfaces.

**Diagram source:** `docs/diagrams/seq_leave_approval.puml`

**Diagram image:** `docs/diagrams/seq_leave_approval.png`

![Leave Approval Sequence Diagram](diagrams/seq_leave_approval.png)

The existing UI mockups in `docs/diagrams/ui/` may also include the dashboard, room, and fees screens.

### 4.6 Open Issues and Future Enhancements

The following items may be considered for future versions and are not assumed to be part of the current implementation:

1. Email or SMS notifications for complaint updates and leave decisions.
2. Integration with an online payment gateway.
3. Exporting administrative reports to CSV or PDF.
4. Additional database indexing and performance optimization based on measured workloads.
5. A dedicated mobile application.

These enhancements should be prioritized based on user feedback, technical feasibility, and project requirements.

## 5. Appendices

### Appendix A: Glossary

| Term | Meaning |
|---|---|
| HMS | Hostel Management System |
| RBAC | Role-Based Access Control |
| MVT | Model-View-Template, Django's architectural pattern |
| ORM | Object-Relational Mapping |
| CSRF | Cross-Site Request Forgery |
| STRIDE | A security threat-modeling framework |
| UML | Unified Modeling Language |
| SRS | Software Requirements Specification |
| SAD | Software Architecture Document |
| STP | Software Test Plan |
| NFR | Non-Functional Requirement |

### Appendix B: References

1. IEEE 42010, *Systems and Software Engineering — Architecture Description*.
2. OWASP, *OWASP Top 10 Web Application Security Risks*.
3. Django documentation: https://docs.djangoproject.com/
4. Jackfruit Hostel Management System, Software Requirements Specification.
5. Jackfruit Hostel Management System, Software Test Plan.

### Appendix C: Tools

| Tool | Purpose |
|---|---|
| GitHub | Source control and collaboration |
| PlantUML | UML sequence diagram source files |
| diagrams.net (draw.io) | Architecture and design diagrams |
| Postman | HTTP endpoint testing, if applicable |
| Django test framework | Automated application testing |
| JMeter or Locust | Performance testing, as applicable |

The tools listed above are intended for design and testing activities; their inclusion does not imply that every tool has already been used.
