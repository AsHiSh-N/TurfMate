# 2026-10-02: Phase 1 MVP stabilization

## Scope

Stabilize existing TurfMate customer, owner, and admin workflows without adding product capabilities. The work addressed observed runtime/build failures, request validation, booking consistency, frontend error presentation, and regression coverage.

## Root causes and fixes

- Frontend HTTP 500: Next development and production builds shared `.next`; running `next build` while a development process was serving that directory left webpack manifests referencing missing chunks (including `./138.js`). Development now uses `.next-dev`, production uses `.next`, and Playwright uses `.next-e2e`.
- Local browser/API mismatch: CORS allowed `localhost:3000` but not the actual `127.0.0.1:3000` origin. Local loopback aliases are now allowed only when the configured frontend origin is local; non-local configured origins remain explicit.
- Booking correctness: the server now requires future exact one-hour slots between 06:00 and 23:00, validates active venue and matching court/activity, rejects active blocks and overlapping confirmed bookings, and determines user ID and the fixed amount itself.
- Availability consistency: only active venues expose availability; elapsed slots, active blocks, and confirmed bookings are unavailable, while cancelled bookings release the slot.
- Owner blocks: ownership is enforced, invalid intervals are rejected, and confirmed bookings cannot be blocked.
- Frontend errors/date selection: shared API error mapping presents unavailable API, authorization, validation, conflict, not-found, and server errors; changing the selected date fetches that date rather than the prior state value.
- Dependencies: Next.js 16.3.8 and PostCSS 8.5.23 replaced vulnerable versions; `npm audit` reports zero vulnerabilities.

## Concurrency and data behavior

SQLite booking creation uses `BEGIN IMMEDIATE` for the conflict check plus booking/payment inserts. A file-backed concurrent regression test confirms two simultaneous same-slot requests return one success and one conflict. This serializes SQLite writes database-wide; other database dialects have no equivalent locking or interval exclusion constraint in this MVP.

Payment remains mock-only. Booking cancellation changes booking status; it does not refund or change the mock payment's `PAID` status.

## Database and Compose

Tables are still initialized using `Base.metadata.create_all()`. There is no active Alembic configuration or Python revision, and no schema changed in this stabilization; a migration baseline is recommended before future schema evolution against existing databases.

Compose YAML parses with duplicate-key checking and currently defines `backend` and `frontend` services. Docker CLI is unavailable here, so Docker Compose configuration execution, image build, and container startup are blocked and not claimed as passing.

## Verification

- Backend pytest suite: `9 passed, 1 warning in 1.46s` on the final full-suite run, including timezone-offset input coverage.
- Frontend `npm run typecheck`: passed.
- Frontend `npm run typecheck` and `npm run build`: passed on Next.js 16.3.8.
- Production build run while dev server was active: all five live routes continued returning HTTP 200.
- Live backend: health returned `{"status":"ok"}` and browser preflight for `http://127.0.0.1:3000` returned HTTP 200 with the matching allow-origin header.
- Frontend `/`, `/login`, `/bookings`, `/owner`, and `/admin`: all returned HTTP 200 on `127.0.0.1:3000`.
- Playwright: customer login/discovery/availability/booking/history/cancellation, protected-page authentication feedback, and API-unavailable feedback all passed (`3 passed` in 18.8s) using the stable isolated E2E output path.
- `npm audit --audit-level=high`: zero vulnerabilities.
- Compose YAML duplicate-key parse: valid; Docker runtime execution blocked because Docker CLI is unavailable.

## Deferred

Real payments/refunds, configurable pricing or operating hours, venue/court management, owner blocking UI, privileged owner/admin E2E flows, database migrations, production secrets/deployment hardening, and cross-database concurrency enforcement remain out of scope.
