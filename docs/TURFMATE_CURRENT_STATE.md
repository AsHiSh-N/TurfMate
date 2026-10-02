# TurfMate Current State Snapshot

## 1. Current product scope

This repository currently represents a local MVP for sports venue discovery and booking. It is not a production booking platform and does not include real payment processing or advanced venue operations.

## 2. Current architecture

The project is a modular monolith split between a Next.js frontend and a FastAPI backend.

- Frontend: Next.js App Router + React + TypeScript
- Backend: FastAPI + SQLAlchemy + SQLite
- Auth: JWT bearer tokens + PBKDF2 hashed passwords
- Database: SQLite by default, with a local DB file in the backend folder

## 3. Current technology stack

- Python 3.13 / FastAPI 0.141.1
- SQLAlchemy 2.0.54
- Pydantic + pydantic-settings
- python-jose + passlib
- SQLite default database
- Next.js 16.3.8, React 18.3.1
- TypeScript 5.5.4
- pytest + FastAPI TestClient

## 4. Current user roles

- CUSTOMER
- VENUE_OWNER
- ADMIN

## 5. Current screens and routes

- `/` - customer discovery and booking screen
- `/login` - login and role-based redirect
- `/bookings` - customer booking history and cancellation
- `/owner` - owner venue submission and venue list
- `/admin` - admin venue approval and read-only reports

## 6. Current APIs

### Public
- `GET /health`
- `GET /api/activities`
- `GET /api/venues`
- `GET /api/venues/{venue_id}/availability`

### Auth
- `POST /api/auth/login`
- `POST /api/auth/register`

### Customer
- `POST /api/bookings`
- `GET /api/bookings`
- `POST /api/bookings/{booking_id}/cancel`

### Owner
- `GET /api/owner/venues`
- `POST /api/owner/venues`
- `POST /api/owner/availability/block`

### Admin
- `GET /api/admin/venues`
- `POST /api/admin/venues/{venue_id}/approve`
- `GET /api/admin/bookings`
- `GET /api/admin/payments`

## 7. Current database

Important tables and models currently in code:

- `users`
- `activities`
- `venues`
- `courts`
- `bookings`
- `payments`
- `blocked_slots`

Important relationships:
- User owns venues and makes bookings
- Venue has courts and bookings
- Court belongs to venue and activity
- Booking belongs to user, venue, court, and activity
- Payment belongs to booking
- BlockedSlot belongs to court

## 8. Current authentication

- Login verifies the user record and password hash.
- Passwords are hashed with PBKDF2 via Passlib.
- Tokens are JWT bearer tokens carrying the user ID as the JWT subject.
- Protected APIs decode the bearer token and validate the role record in the database.
- Missing, invalid, and expired bearer tokens return HTTP 401; role mismatch returns HTTP 403.

## 9. Current authorization

- Booking routes require the authenticated user to have role `CUSTOMER`.
- Owner routes require `VENUE_OWNER`.
- Admin routes require `ADMIN`.
- The app does not implement a route guard at the frontend level; it relies on backend checks and localStorage token presence.

## 10. Customer flows

### Discovery
- Search by city and activity
- List active venues
- View generated slots by date

### Booking
- Select a venue and court
- Select a slot
- Submit `POST /api/bookings`
- Booking response includes a generated reference and mock payment status

### Booking history
- `GET /api/bookings`
- `POST /api/bookings/{booking_id}/cancel`

## 11. Owner flows

- Owner signs in
- Submits venue with name, address, city, state, pincode, and one court
- Venue is created in `PENDING` status
- Owner may list their venues
- Blocked-slot API exists but is not exposed to a working UI form

## 12. Admin flows

- Admin signs in
- Lists all venues, bookings, and payment records
- Approves venues, changing the status to `ACTIVE`

## 13. Current booking flow

The live booking flow implemented in code is:

1. customer logs in via `/login`
2. frontend stores JWT in localStorage
3. customer loads venue list and selected availability
a. `GET /api/venues?city=...&activity=...`
4. frontend requests `GET /api/venues/{venue_id}/availability?date=...`
5. frontend posts to `POST /api/bookings`
6. backend validates:
   - user role is `CUSTOMER`
   - venue exists and is `ACTIVE`
   - court belongs to venue and activity
  - date and start time are in the future
  - slot is an exact one-hour interval between 06:00 and 23:00
  - interval does not overlap an active block or existing confirmed booking
  - user ID and fixed total are determined by the backend, not client fields
7. booking record is inserted and a mock payment row is created
8. frontend displays confirmation from the booking response body

## 14. Current test coverage

Implemented tests:
- `backend/tests/test_platform_smoke.py`
  - owner/admin/customer happy path verification
  - valid/invalid login, missing/invalid/expired token validation
  - role boundaries and owner/customer object ownership
  - active/pending venue behavior and invalid schedule/court/activity
  - booking-aware availability, blocks, cancellation release, repeated cancel
  - simultaneous SQLite booking submissions
  - seed smoke assertion

Command run and result:
- `cd /home/ashish/Documents/turf/backend && .venv/bin/python -m pytest -q`
- Result: `9 passed, 1 warning in 1.46s` (final full-suite rerun)

Additional live validation:
- All routes `/`, `/login`, `/bookings`, `/owner`, `/admin` on `http://127.0.0.1:3000` returned HTTP 200.
- `npm run typecheck` and `npm run build` passed with Next.js 16.3.8.
- `npm audit --audit-level=high` reported zero vulnerabilities.
- Compose YAML passed duplicate-key parsing; Docker CLI is unavailable for runtime config/build validation.

## 15. E2E coverage

Playwright Test is configured with isolated frontend/backend ports and a temporary seeded SQLite DB. The customer booking/cancellation journey, protected page auth feedback, and API outage feedback passed in the latest E2E run; owner/admin privileged workflows are not covered.

## 16. Known issues

- Docker runtime validation is blocked in this environment because the `docker` CLI is not installed
- No active Alembic configuration or Python revision exists; tables are created using `Base.metadata.create_all()`
- SQLite booking lock serializes database writes globally; no cross-database interval constraint exists
- Payment processing is mock-only
- Slot price (400) and operating hours (06:00–23:00) are hardcoded MVP rules enforced server-side; distance remains a hardcoded display value
- Owner/admin privileged E2E flows are not covered

## 17. Known limitations

- No real payment gateway
- No profile/account features
- No venue editing or court management UI
- No owner analytics or revenue dashboards
- No admin user management
- No production security hardening or environment secret management beyond local examples

## 18. Mock functionality

- Payment records use `MOCK-` transaction IDs
- Booking totals are fixed at `400` and the backend ignores client-supplied prices
- Availability slots are generated at one-hour intervals from 06:00 to 23:00 with fixed pricing
- Distance is a hardcoded display value; rating is stored on the venue and seeded with demo data

## 19. Environment requirements

Current local development assumptions:
- backend `.env` or default config for local SQLite
- frontend `.env.local` for `NEXT_PUBLIC_API_URL`
- backend running on `127.0.0.1:8000`
- frontend dev server on `127.0.0.1:3000` or the next available port if occupied

## 20. Current implementation status matrix

| Area | Status |
|---|---|
| Venue discovery | IMPLEMENTED |
| Availability | IMPLEMENTED |
| Booking creation | IMPLEMENTED |
| Booking history | IMPLEMENTED |
| Booking cancellation | IMPLEMENTED |
| Owner venue submission | IMPLEMENTED |
| Owner slot blocking API | PARTIALLY IMPLEMENTED |
| Admin approval | IMPLEMENTED |
| Payment processing | MOCK / PLACEHOLDER |
| Profile/account management | NOT IMPLEMENTED |
| E2E tests | PARTIALLY IMPLEMENTED | Playwright customer flow and error-state checks |

## Current system status

IMPLEMENTATION STATUS: PARTIAL / MVP
TEST STATUS: PASS — backend 9 passed; frontend typecheck/build passed; E2E 3 passed
DOCUMENTATION STATUS: UPDATED
E2E STATUS: PARTIAL — customer core flow covered; privileged owner/admin workflows not covered
