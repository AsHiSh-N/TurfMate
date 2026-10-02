# Test Results

## Existing automated tests

The repository contains backend API tests in `backend/tests/test_platform_smoke.py` and an in-memory SQLite fixture. Playwright Test provides isolated browser E2E coverage with a temporary file-backed SQLite database.

### Commands run

1. Backend test suite
```bash
cd /home/ashish/Documents/turf/backend && .venv/bin/python -m pytest -q
```
Result:
- `9 passed, 1 warning in 1.46s` (final full-suite run, including timezone-offset validation).
- The warning comes from the current `pytest-asyncio` configuration and did not fail the suite.

2. Frontend compile/build validation
```bash
cd /home/ashish/Documents/turf/frontend && npm run typecheck && npm run build
```
Result:
- TypeScript checking succeeded
- Next.js 16.3.8 production build succeeded using Turbopack
- Five app routes were generated for `/`, `/admin`, `/bookings`, `/login`, and `/owner`

3. Live frontend route validation
```bash
for route in / /login /bookings /owner /admin; do curl -sS -o /dev/null -w "%{http_code} $route\\n" "http://127.0.0.1:3000$route"; done
```
Result:
- All five routes returned `200` on `http://127.0.0.1:3000` after starting the current Next.js version.

4. Playwright E2E
```bash
cd /home/ashish/Documents/turf/frontend && npm run e2e -- --workers=1
```
Result:
- `3 passed (18.8s)` after stabilizing the E2E output path.
- Coverage: customer login → discovery → date/availability → booking confirmation → booking history → cancellation; unauthenticated protected pages; API-unavailable discovery state.

5. Dependency and Compose validation
- `npm audit --audit-level=high` -> `found 0 vulnerabilities`
- Docker Compose YAML parsed with duplicate-key rejection -> valid services `backend`, `frontend`
- Docker CLI is unavailable, so `docker compose config` and container build/start were not executable.

## What is actually covered

- Owner/admin/customer happy-path role flow is tested in `test_owner_admin_customer_happy_path`
- Duplicate booking and repeat-cancel rejection are covered in `test_duplicate_booking_and_repeat_cancel_are_rejected`
- Input validation and invalid token checks are present in `test_invalid_login_and_invalid_token`
- A basic seed/idempotence check exists in `test_seed_is_runnable_and_idempotent`

## E2E coverage status

- Playwright Test configuration and the core customer booking/cancellation flow are implemented.
- Additional E2E checks cover unsigned `/bookings`, `/owner`, and `/admin` responses plus API outage feedback.
- E2E does not cover privileged owner/admin workflows or production payment behavior.

## Test status summary

- Backend tests: PASS
- Frontend TypeScript/build validation: PASS
- Live frontend routes: PASS on `http://127.0.0.1:3000`
- Docker validation: BLOCKED — Docker CLI not installed in this environment
- E2E flow coverage: IMPLEMENTED; 3 flows passed in 18.8s
- Dependency audit: PASS — zero vulnerabilities
