### STP-P4-1: Complaints and Leave Management — Test Scope

The Complaints and Leave Management module covers student complaint submission, administrator complaint status updates, student leave request submission, and administrator leave request decisions.

The features will be tested against the corresponding SRS requirements:

- **REQ-17:** Verify that a student can submit a complaint associated with their allocated room.
- **REQ-18:** Verify that an administrator can update a complaint status to In-progress or Resolved.
- **REQ-19:** Verify that a student can submit a leave request with a valid date range and reason.
- **REQ-20:** Verify that an administrator can approve or reject a pending leave request.

Testing will also cover input validation, access control, and rejection of invalid operations. Tests will use authorized student and administrator accounts and will record actual results after the relevant features are implemented.

<!-- STP-P1-1 -->

## 3. Features to be Tested

Features are mapped to SRS requirement IDs.

<!-- STP-P1-2 -->
<!-- STP-P2-1 -->
<!-- STP-P3-1 -->
### STP-P4-2: Complaint and Leave Functional Testing

The following functional features will be tested:

- **Complaint submission:** A student submits a complaint with a description. The system should associate it with the student's allocated room.
- **Complaint status management:** An administrator changes a complaint status to In-progress or Resolved. The system should save the updated status.
- **Leave request submission:** A student submits a leave request containing a reason, start date, and end date. The system should validate the date range and create the request with Pending status.
- **Leave request decision:** An administrator approves or rejects a pending leave request. The system should save the decision and prevent a second decision from being applied to an already processed request.
- **Validation and authorization:** The system should reject invalid input and prevent unauthorized users from accessing restricted operations.

<!-- STP-P2-2 -->

<!-- STP-P2-3 -->

<!-- STP-P1-3 -->

<!-- STP-P1-4 -->

<!-- STP-P3-2 -->

<!-- STP-P3-3 -->

<!-- STP-P3-4 -->

<!-- STP-P3-5 -->

<!-- STP-P2-4 -->

<!-- STP-P2-5 -->

### STP-P4-3: Test Environment and Test Data

Testing will be performed in the Jackfruit Hostel Management System's test environment using the configured Django application and PostgreSQL database.

**Test accounts:**
- Student account with a valid allocated room.
- Administrator account with permission to manage complaints and leave requests.
- Student account without a valid room allocation, where applicable.

**Test data:**
- A complaint containing a valid description.
- A leave request with a valid start date, end date, and reason.
- A leave request with an invalid date range.
- Complaints with Open, In-progress, and Resolved statuses, as supported by the implementation.
- Pending, Approved, and Rejected leave requests.

Tests should use non-production data. Actual results will be recorded after the corresponding features are implemented and tested.
<!-- STP-P3-6 -->

### STP-P4-4: Test Approach and Expected Outcomes

Testing will verify normal operations, invalid inputs, and access restrictions for the Complaints and Leave Management module.

- **Positive testing:** Submit valid complaints and leave requests, update complaint statuses, and approve or reject pending leave requests.
- **Negative testing:** Submit requests with missing required fields, invalid leave date ranges, or invalid status values. The system should reject invalid requests with an appropriate response.
- **Authorization testing:** Verify that students cannot perform administrator-only actions and administrators cannot perform student-only actions unless explicitly permitted by the application.
- **State validation:** Verify that leave decisions can be made only for pending requests and that processed requests cannot be decided again.
- **Data consistency:** Verify that successfully submitted complaints and leave requests are persisted correctly in the database.

The actual results and Pass/Fail status will be documented after test execution. Any failures will be recorded for correction and retesting.

## 16. Test Cases

Each test case lists the requirement it verifies, its level (Unit, Integration or System), pre-conditions, steps, test data and the expected result. Actual Result and Pass/Fail are filled after execution on the implemented feature.

<!-- STP-P1-5 -->

<!-- STP-P2-6 -->

<!-- STP-P3-7 -->

### STP-P4-5: Complaints and Leave Management Test Cases

#### TC-P4-01: Submit a Complaint

- **Requirement:** REQ-17
- **Level:** Integration
- **Preconditions:** The student is authenticated and has an allocated room.
- **Steps:**
  1. Log in as a student.
  2. Open the complaints section.
  3. Enter a valid complaint description and submit it.
  4. Verify the saved complaint.
- **Test Data:** Description: "Water leakage in the bathroom."
- **Expected Result:** The complaint is saved successfully and associated with the student's allocated room.

#### TC-P4-02: Update Complaint Status

- **Requirement:** REQ-18
- **Level:** Integration
- **Preconditions:** A complaint exists, and an administrator is authenticated.
- **Steps:**
  1. Log in as an administrator.
  2. Open the complaint.
  3. Change its status to In-progress.
  4. Save and verify the updated status.
  5. Repeat with Resolved.
- **Test Data:** Status values: In-progress and Resolved.
- **Expected Result:** The administrator can update the complaint status, and each change is saved correctly.

#### TC-P4-03: Submit a Valid Leave Request

- **Requirement:** REQ-19
- **Level:** Integration
- **Preconditions:** The student is authenticated.
- **Steps:**
  1. Log in as a student.
  2. Open the leave request section.
  3. Enter a valid start date, end date, and reason.
  4. Submit the request.
  5. Verify the saved request.
- **Test Data:** Start date: 20-10-2026; End date: 22-10-2026; Reason: Family function.
- **Expected Result:** The leave request is saved with Pending status and the submitted details are stored correctly.

#### TC-P4-04: Reject an Invalid Leave Date Range

- **Requirement:** REQ-19
- **Level:** Integration
- **Preconditions:** The student is authenticated.
- **Steps:**
  1. Open the leave request form.
  2. Enter an end date earlier than the start date.
  3. Submit the request.
- **Test Data:** Start date: 22-10-2026; End date: 20-10-2026.
- **Expected Result:** The system rejects the invalid date range and does not create a leave request.

#### TC-P4-05: Approve a Pending Leave Request

- **Requirement:** REQ-20
- **Level:** Integration
- **Preconditions:** A leave request has Pending status, and an administrator is authenticated.
- **Steps:**
  1. Log in as an administrator.
  2. Open the pending leave request.
  3. Approve the request.
  4. Verify the saved decision.
- **Test Data:** A valid pending leave request.
- **Expected Result:** The request status changes to Approved and the decision is saved.

#### TC-P4-06: Reject a Pending Leave Request

- **Requirement:** REQ-20
- **Level:** Integration
- **Preconditions:** A leave request has Pending status, and an administrator is authenticated.
- **Steps:**
  1. Log in as an administrator.
  2. Open the pending leave request.
  3. Reject the request.
  4. Verify the saved decision.
- **Test Data:** A valid pending leave request.
- **Expected Result:** The request status changes to Rejected and the decision is saved.

#### TC-P4-07: Prevent Unauthorized Complaint Status Updates

- **Requirement:** REQ-18
- **Level:** System
- **Preconditions:** A student is authenticated, and a complaint exists.
- **Steps:**
  1. Log in as a student.
  2. Attempt to update the complaint status using the restricted operation.
- **Test Data:** An existing complaint and a student account.
- **Expected Result:** The system denies the unauthorized operation, and the complaint status remains unchanged.

#### TC-P4-08: Prevent Decisions on Processed Leave Requests

- **Requirement:** REQ-20
- **Level:** Integration
- **Preconditions:** A leave request has already been Approved or Rejected.
- **Steps:**
  1. Log in as an administrator.
  2. Attempt to make another decision on the processed request.
  3. Verify the stored status.
- **Test Data:** A leave request already marked Approved or Rejected.
- **Expected Result:** The system rejects the second decision, and the original status remains unchanged.

**Execution record:** Actual Result: To be filled during execution. Pass/Fail: To be filled during execution.
