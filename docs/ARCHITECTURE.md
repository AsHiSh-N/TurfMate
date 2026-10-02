# Architecture

## Overview

TurfMate is implemented as a simple modular monolith with a Next.js frontend and a FastAPI backend sharing a SQLite default database. There is no separate service layer, repository layer, or production-grade queue system in the current codebase.

## Runtime architecture

```text
Browser (Next.js App Router)
  -> frontend pages and client-side fetch calls
       -> FastAPI router handlers
            -> SQLAlchemy ORM session
                 -> SQLite database
```

## Frontend

The frontend uses Next.js 16.3.8, React 18.3.1, and TypeScript. Its client-side screens under `frontend/app` are:
- `/` customer discovery
- `/login` login
- `/bookings` bookings listing
- `/owner` owner submission/listing
- `/admin` admin venue and reporting screen

The shared nav component is in `frontend/components/PortalNav.tsx`.

## Backend

The backend bootstrap is in `backend/app/main.py`. It:
- creates the FastAPI app
- configures CORS
- registers route modules for auth, venues, bookings, owner, and admin
- creates tables via `Base.metadata.create_all()`

## Core modules

- `backend/app/core/config.py` — settings from `.env`
- `backend/app/core/security.py` — JWT creation, password hashing, token validation
- `backend/app/db/session.py` — SQLAlchemy engine and session creation
- `backend/app/models/__init__.py` — ORM model definitions
- `backend/app/api/*/routes.py` — route handlers
- `backend/app/core/booking_rules.py` — shared fixed MVP schedule and price rules

## Authentication and authorization flow

- Login validates email and password
- Token is issued with the user ID as the JWT subject
- Protected APIs call `get_current_user()` and then role-check the user record
- Role checks are enforced in the route functions:
  - `CUSTOMER` for bookings
  - `VENUE_OWNER` for owner operations
  - `ADMIN` for admin operations

## Data flow

Customer discovery flow:
1. frontend calls `GET /api/venues?city=...&activity=...`
2. venue route filters `Venue` rows where status is `ACTIVE`
3. UI renders active venue cards
4. frontend calls `GET /api/venues/{id}/availability?date=...`
5. availability route generates one-hour slots from 06:00 to 23:00, marking elapsed, confirmed-booking, and blocked intervals unavailable
6. booking call posts to `POST /api/bookings`
7. route validates the customer, future date/time, slot window, active venue, venue/court/activity relationship, blocked intervals, and existing confirmed overlaps; it sets the fixed server-side amount and inserts a booking plus mock payment record

For SQLite, booking creation acquires a `BEGIN IMMEDIATE` write transaction before checking conflicts and holds it through the booking/payment commit. The concurrent regression test against a file-backed SQLite database confirms one winner and one 409 response for two simultaneous same-slot requests. This serializes SQLite writes database-wide and is not a portable database exclusion constraint.

## Current limitations

- No service layer or repository abstraction
- No real refund, payment, or booking ledger process
- The SQLite immediate write transaction protects the current local booking path; non-SQLite databases have no equivalent lock or database-level overlap constraint in this implementation
- No real operating-hours or pricing rules
- Schema initialization uses `Base.metadata.create_all()`; no Alembic configuration or Python revision is active
- Development, production, and Playwright builds use separate `.next-dev`, `.next`, and `.next-e2e` directories to prevent concurrent build artifact collisions

## Current status

IMPLEMENTATION STATUS: PARTIAL / MVP

This architecture is suitable for local demonstration and initial product validation, not for production-grade scale or payment operations.
