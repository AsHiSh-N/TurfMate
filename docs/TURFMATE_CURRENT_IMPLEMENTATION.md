# TurfMate - Current Implementation Baseline

This is the repository source-of-truth document for the current implementation. It is grounded in the actual code present in the workspace and in direct runtime checks performed during the current audit.

Status labels: IMPLEMENTED, PARTIALLY IMPLEMENTED, MOCK / PLACEHOLDER, IMPLEMENTED WITH KNOWN ISSUE, NOT IMPLEMENTED.

## 1. Product scope

The current product is a local MVP for sports venue discovery and booking. Customers can search active venues by city and activity, view generated hourly availability, and create a booking after sign-in. Venue owners can submit a venue and list their own venues. Admins can review and approve venues and read payment and booking records.

## 2. Current implementation status

### Implemented
- Next.js app with customer, login, owner, and admin screens
- FastAPI backend with router registration and CORS
- SQLAlchemy ORM models for users, activities, venues, courts, bookings, payments, and blocked slots
- JWT authentication using bearer tokens
- PBKDF2 password hashing
- Venue discovery and availability generation
- Booking creation, listing, and cancellation scoped to the authenticated customer
- Future one-hour schedule validation, active venue/court/activity checks, server-owned price and user ID, block/conflict rejection, and booking-aware availability
- SQLite `BEGIN IMMEDIATE` serialization around booking conflict-check plus inserts
- Venue approval flow for admin users
- SQLite-backed local dev configuration
- Demo seed data for customer, owner, admin, activity, and a seeded venue
- Backend regression suite and Playwright customer E2E foundation
- Frontend API error states for unavailable API, auth/role denial, validation, conflict, not found, and server failure
- Next.js development/production/E2E output directories are isolated
- Live frontend routes return `HTTP 200`; production build succeeds
- Next.js/PostCSS security update; current `npm audit` reports zero vulnerabilities

### Partially implemented
- Dedicated venue detail page and API
- Owner slot-block UI
- Role-based screens and route experiences beyond the basic pages
- Configurable booking availability based on stored operating hours / pricing rules
- Admin moderation beyond approve-only flows

### Mock / placeholder
- Payment records are inserted as mock paid records (`MOCK-...` transaction IDs)
- Price is fixed at 400 for all slots and enforced server-side
- Opening hours are fixed at 06:00–23:00
- Distance remains a hardcoded display value; rating comes from the stored venue field/seed data
- Seed data is intentionally demo-only

### Not implemented
- Real payment gateway
- Profile/account management
- Venue editing or removal
- Court management screen
- Dashboard analytics for owners
- Admin user management
- Privileged owner/admin E2E workflows
- Production deployment protections

## 3. Current routes and screens

- `/` - customer discovery and booking
- `/login` - sign-in and token storage
- `/bookings` - customer booking list and cancel flow
- `/owner` - owner venue submission and listing
- `/admin` - admin venue approval and reporting

## 4. Verified runtime status

Verified commands and results:
- `cd /home/ashish/Documents/turf/backend && .venv/bin/python -m pytest -q` -> `9 passed, 1 warning in 1.46s` (final full-suite rerun)
- `cd /home/ashish/Documents/turf/frontend && npm run typecheck && npm run build` -> succeeded
- `cd /home/ashish/Documents/turf/frontend && npm run e2e -- --workers=1` -> core customer flow, protected-page auth messaging, and API outage flow passed
- `cd /home/ashish/Documents/turf/frontend && npm audit --audit-level=high` -> zero vulnerabilities
- All five frontend routes on `http://127.0.0.1:3000` -> HTTP 200
- Compose YAML parser with duplicate-key rejection -> valid; Docker CLI unavailable for Compose runtime validation

## 5. Important known issues

- Docker validation is blocked in this environment because the Docker CLI is not installed.
- E2E covers the core customer journey and error states but not owner/admin privileged workflows.
- Schema is created with `Base.metadata.create_all()`; there is no active migration configuration or revision. Existing tables are not evolved by `create_all()`.
- SQLite `BEGIN IMMEDIATE` serializes writers database-wide; other database dialects have no concurrency-safe slot exclusion.
- Payments remain mock `PAID` records; cancellation does not refund or alter payment status.

## 6. Technical stack

- Backend: FastAPI, SQLAlchemy, SQLite
- Frontend: Next.js, React, TypeScript
- Auth: JWT + Passlib PBKDF2-SHA256
- Testing: pytest + FastAPI TestClient
- Environment: local `.env` and `.env.local` files

## 7. Current status matrix

| Area | Status |
|---|---|
| Customer discovery | IMPLEMENTED |
| Availability generation | IMPLEMENTED |
| Booking | IMPLEMENTED |
| Customer booking history | IMPLEMENTED |
| Owner venue submission | IMPLEMENTED |
| Owner slot block API | PARTIALLY IMPLEMENTED |
| Admin approval | IMPLEMENTED |
| Payment integration | MOCK / PLACEHOLDER |
| Production-grade security | NOT IMPLEMENTED |
| E2E coverage | PARTIALLY IMPLEMENTED | Customer booking/cancellation and selected error-state flows |

The detailed API and database inventories are in [docs/API.md](API.md), [docs/DATABASE.md](DATABASE.md), and [docs/TURFMATE_CURRENT_STATE.md](TURFMATE_CURRENT_STATE.md).
