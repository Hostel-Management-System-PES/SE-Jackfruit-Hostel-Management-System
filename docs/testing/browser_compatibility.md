# Browser compatibility checklist: NFR-5

**Requirement (NFR-5):** The system shall work without functional differences on the latest versions of Chrome and Firefox.

**Owner:** P2 (Prathiksha)

**How to test:**

1. Run the app with `python manage.py runserver`.
2. Do every row below once in Chrome and once in Firefox.
3. Write the browser version (Chrome: `chrome://version`, Firefox: `about:support`).
4. Mark each cell Pass or Fail. For a Fail, write what went wrong under Notes.

**Chrome version:** 156.0.8078.80

**Firefox version:** 159.0.1

**Tested by:** Prathiksha B P

**Date:** 07-11-2026

| # | Page / action | What to check | Chrome | Firefox | Notes |
|---|---|---|---|---|---|
| 1 | Register | Form shows errors in red under each field; valid form shows the Pending message | pass|pass | |
| 2 | Login with email | Goes to the correct dashboard | pass|pass | |
| 3 | Login with SRN | Goes to the student dashboard | pass|pass | |
| 4 | Admin dashboard | Cards and Pending registrations table show; Approve / Reject work | pass|pass | |
| 5 | Rooms & Blocks | Add block, add room, edit room; badges show Vacant / Occupied | pass|pass | |
| 6 | Room Allocation | Allocate a student; Deallocate button frees the bed |pass |pass | |
| 7 | Fees | Date picker opens for Payment date; record payment; set fee | pass|pass | |
| 8 | Dues Report | Totals show; "Show only students with dues" filter works | pass|pass | |
| 9 | Complaints & Leave (admin) | In-progress / Resolved buttons; Approve / Reject leave |pass |pass | |
| 10 | Audit Log | Table shows events; Filter drop-down works | pass|pass | |
| 11 | Student dashboard | Room, fee, complaint and leave cards show |pass |pass | |
| 12 | My Room | Room details and "Raise a complaint" button |pass |pass | |
| 13 | Fee Details | Fee, Total paid, Outstanding cards; payment history table |pass |pass | |
| 14 | Complaints & Leave (student) | File a complaint; leave date pickers open; submit leave |pass |pass | |
| 15 | My Profile | Edit name and guardian contact; success message shows |pass |pass | |
| 16 | Wrong role | A student opening `/rooms/` sees the 403 page |pass |pass | |
| 17 | Logout | Goes back to login; the Back button does not show the dashboard data |pass |pass | |
| 18 | Narrow window | Shrink the window to phone width; tables scroll sideways, nothing overlaps |pass |pass | |

**Result:** NFR-5 passes when every row is Pass in both browsers.
