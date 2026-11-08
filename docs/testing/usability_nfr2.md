# Usability walkthrough: NFR-2 (TC-USE-01)

**Requirement (NFR-2):** A student shall be able to file a complaint in no more than 4 screens, starting from the dashboard.

**Owner:** P4 (Varsha)

## Automated check

`complaints/tests/test_usability.py` follows the same links a student clicks and counts the pages. It fails if the count goes above 4.

```
pytest complaints/tests/test_usability.py
```

## Manual walkthrough

**Setup:**

- A new student account, verified by the admin.
- A room allocated to that student.
- The student is logged in.

**Steps:**

| Screen | What the student sees | What the student does |
|---|---|---|
| 1 | Student Dashboard | Clicks **Complaints & Leave** in the left menu |
| 2 | Complaints & Leave page, with the "New complaint" form | Types the issue and clicks **Submit complaint** |
| 3 | Same page, with the green message "Your complaint was submitted and is Open." and the complaint in the list | Done |

**Other route:** Dashboard, then **My Room**, then **Raise a complaint for this room**, then submit. That route takes 4 screens, which is still within the limit.

## Result

| Test case | Expected | Actual | Status |
|---|---|---|---|
| TC-USE-01 | No more than 4 screens | 3 screens (4 using the My Room route) | Pass |

Walkthrough done by: Varsha Patil
Date: 08 November 2026
