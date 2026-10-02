# Changelog

## 2026-10-02 — Phase 1 MVP stabilization

### Updated
- Isolated Next.js development, production, and E2E output directories to prevent build artifact collisions that caused missing webpack chunks and HTTP 500 responses.
- Fixed local CORS for the `127.0.0.1` frontend origin and centralized user-facing API error mapping.
- Enforced future hourly booking windows, active venue/court/activity relationships, owner blocks, booking conflicts, backend-owned user/price values, and booking-aware availability.
- Preserved SQLite `BEGIN IMMEDIATE` serialization and added a concurrent same-slot regression test.
- Updated Next.js to 16.3.8 and PostCSS to 8.5.23; full npm audit reports zero vulnerabilities.
- Added Playwright customer booking/cancellation and error-state E2E coverage.
- Updated API, architecture, database, state, implementation, and test documentation.

### Verification
- Backend: `9 passed, 1 warning`
- Frontend: typecheck and production build passed; all five routes returned HTTP 200
- E2E: 3 flows passed in 18.8s using the stable isolated E2E output path
- Compose YAML: parsed with duplicate-key rejection; Docker runtime validation unavailable because Docker CLI is not installed

### Remaining limitations
- No active database migration chain; schema setup remains `create_all()`.
- E2E does not exercise privileged owner/admin workflows.
- Pricing/operating hours remain fixed MVP rules, payment remains mock, and SQLite serialization is database-wide and not portable to other dialects.

## 2026-10-02 — Baseline audit completed

### Updated
- Verified the current repository state against the actual code and runtime behavior.
- Recorded the current implementation status without assuming planned features exist.
- Updated the source-of-truth documentation to reflect actual routes, models, auth rules, and test results.

### Current repository status
- Backend: implemented and passing the current backend smoke tests
- Frontend: compiling and producing the app routes
- API: 16 routes registered in the current FastAPI app
- Database: 7 core ORM tables present
- Live frontend routes: verified as HTTP 200 on `127.0.0.1:3000`
- Docker validation: blocked in this environment because the `docker` CLI is not installed

### Known issues recorded
- Live frontend route was fixed and verified as returning HTTP 200
- Docker validation is blocked on this machine because Docker is unavailable
- No active migration versions present under Alembic
- No real payment gateway integration
- Playwright E2E suite covers the customer core flow and selected error states

## State label summary

- IMPLEMENTED: customer discovery, booking, owner venue submission, admin approval, JWT auth, SQLite runtime, backend tests
- PARTIALLY IMPLEMENTED: owner block flow, pricing and operating hours configuration, dedicated venue detail pages
- MOCK / PLACEHOLDER: payment processing, price, rating, distance values
- NOT IMPLEMENTED: real payment, profiles, court management, analytics, privileged owner/admin E2E coverage
