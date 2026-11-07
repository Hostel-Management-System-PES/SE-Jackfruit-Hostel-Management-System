# Performance test results: NFR-1 (TC-PERF-01)

**Requirement (NFR-1):** Standard page requests (dashboard, room list, fee view) respond within 2 seconds for 95% of requests with up to 10 concurrent users.

**Owner:** P2 (Prathiksha)

**Tool:** Locust 2.x, script `loadtest/locustfile.py`, test data from `loadtest/seed.py`.

## Setup

- **Seed data:** 50 rooms in 5 blocks, 1 admin, and 10 verified students with fees.
- **Users:** 10 simulated users (8 students and 2 admins). Each user logs in once, then opens pages with 1 to 2 seconds of wait between pages.
- **Ramp-up:** 2 new users per second. The run lasts 1 minute.
- **Server:** Django development server with a SQLite database, on one machine.

**Command:**

```
locust -f loadtest/locustfile.py --host http://127.0.0.1:8000 --headless -u 10 -r 2 -t 1m --csv loadtest/results
```

## Results (run on 06 Nov 2026)

| Page | Requests | Failures | Median (ms) | 95th percentile (ms) | Max (ms) |
|---|---|---|---|---|---|
| Student dashboard | 129 | 0 | 13 | 28 | 56 |
| My Room | 96 | 0 | 10 | 17 | 60 |
| Fee Details | 73 | 0 | 11 | 22 | 56 |
| Room list (availability) | 34 | 0 | 17 | 22 | 27 |
| Admin dashboard | 26 | 0 | 12 | 56 | 60 |
| Fee overview | 13 | 0 | 19 | 28 | 28 |
| Login (POST, once per user) | 10 | 0 | 330 | 370 | 370 |
| **All requests** | **391** | **0** | **12** | **52** | **370** |

Login is slower on purpose. Checking a password runs the PBKDF2 password hash (SEC-1), which is built to be slow. It is still far below 2 seconds.

## Verdict

| Test case | Expected | Actual | Status |
|---|---|---|---|
| TC-PERF-01 | 95% of responses within 2000 ms | 95% within 52 ms, 0 failures | Pass |
