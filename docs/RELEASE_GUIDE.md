# TurfMate Release Guide

This document is the current implementation and usage reference for TurfMate.

## Product overview

TurfMate is a sports venue marketplace for discovering courts, checking live slot availability, and booking sports facilities. The current implementation supports customers, venue owners, and administrators.

## Application screens

### Customer discovery: `/`

The main customer screen provides:

- City search
- Sport filtering for badminton and cricket-compatible activity slugs
- Active venue cards
- Venue rating, location, and starting hourly price
- Availability modal with date selection
- Court-by-court hourly slots
- Disabled slots for blocked availability
- Authenticated booking confirmation
- Mock payment confirmation and booking reference

The page calls:

- `GET /api/venues`
- `GET /api/venues/{venue_id}/availability`
- `POST /api/bookings`

### Login: `/login`

The login screen:

- Authenticates a user through the backend
- Stores the JWT in browser local storage under `turfmate_token`
- Stores the role under `turfmate_role`
- Redirects customers to `/bookings`
- Redirects venue owners to `/owner`
- Redirects administrators to `/admin`

### Customer bookings: `/bookings`

The customer booking workspace provides:

- Authenticated booking history
- Booking reference
- Venue ID
- Date and time range
- Total amount
- Booking status
- Cancellation for confirmed bookings

The page calls:

- `GET /api/bookings`
- `POST /api/bookings/{booking_id}/cancel`

### Venue owner studio: `/owner`

The owner screen provides:

- Owner venue list
- Venue status display
- Venue submission form
- Name, description, address, city, state, pincode, activity, and court name fields
- `PENDING` submission status until admin approval

The page calls:

- `GET /api/owner/venues`
- `POST /api/owner/venues`

The backend also supports owner availability blocking through `POST /api/owner/availability/block`. A dedicated blocking form can be added to the owner screen without changing the API contract.

### Admin console: `/admin`

The admin screen provides:

- Pending venue count
- Total venue count
- Booking count
- Payment count
- Venue approval queue
- Venue owner and city information
- Approve venue action
- Booking oversight list
- Payment oversight list

The page calls:

- `GET /api/admin/venues`
- `POST /api/admin/venues/{venue_id}/approve`
- `GET /api/admin/bookings`
- `GET /api/admin/payments`

## Backend functionality

### Authentication

- Customer registration
- Login for all seeded roles
- JWT access tokens
- Password hashing with PBKDF2-SHA256
- Role-aware frontend redirects
- Protected owner, admin, and booking endpoints

### Venue discovery

- List active venues
- Filter by city
- Filter by activity slug
- Return activity, rating, starting price, and distance fields
- View availability for a selected date
- Generate hourly slots from 06:00 through 23:00
- Mark slots unavailable when a blocked interval overlaps them

### Customer booking

- Requires an authenticated customer token
- Validates venue, court, and activity relationships
- Validates that end time is after start time
- Rejects overlapping confirmed bookings
- Creates a confirmed booking
- Creates a mock paid payment record
- Returns a unique booking reference
- Allows customers to cancel their own bookings

### Venue owner operations

- List venues belonging to the authenticated owner
- Create a venue with its first court
- New venues start in `PENDING` state
- Block an owned venue court for a date/time interval
- Blocked intervals are reflected in public availability

### Admin operations

- List all venues
- Approve a pending venue
- List all bookings
- List all payments

## Roles and permissions

| Capability | Customer | Venue owner | Admin |
|---|---:|---:|---:|
| Discover active venues | Yes | Yes | Yes |
| View availability | Yes | Yes | Yes |
| Create customer booking | Yes | No | No |
| View own bookings | Yes | No | No |
| Cancel own booking | Yes | No | No |
| Submit venue | No | Yes | No |
| View owned venues | No | Yes | No |
| Block owned venue slot | No | Yes | No |
| Approve venues | No | No | Yes |
| View all bookings | No | No | Yes |
| View all payments | No | No | Yes |

## API route inventory

### Public and customer routes

```text
GET  /health
POST /api/auth/login
POST /api/auth/register
GET  /api/activities
GET  /api/venues
GET  /api/venues/{venue_id}/availability
GET  /api/bookings       authenticated
POST /api/bookings       authenticated
POST /api/bookings/{booking_id}/cancel authenticated
```

### Owner routes

```text
GET  /api/owner/venues                  owner token
POST /api/owner/venues                  owner token
POST /api/owner/availability/block      owner token
```

### Admin routes

```text
GET  /api/admin/venues                  admin token
POST /api/admin/venues/{venue_id}/approve admin token
GET  /api/admin/bookings                admin token
GET  /api/admin/payments                admin token
```

Interactive API documentation is available at `http://localhost:8000/docs` when the backend is running.

## Demo credentials

These are local-development credentials only:

| Role | Email | Password |
|---|---|---|
| Customer | `customer@example.com` | `DemoPass123!` |
| Venue owner | `owner@example.com` | `DemoPass123!` |
| Admin | `admin@example.com` | `DemoPass123!` |

## Run locally

### Frontend only

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

The frontend expects the API at `http://localhost:8000/api` by default. Set `NEXT_PUBLIC_API_URL` in `frontend/.env.local` to override it.

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://localhost:8000/docs` for Swagger.

### Docker

```bash
docker compose up --build
```

Open:

- `http://localhost:3000` for the app
- `http://localhost:8000/docs` for the API

## Verification status

The frontend production build was verified with:

```bash
npm run typecheck
npm run build
```

The build generated these routes:

```text
/
/login
/bookings
/owner
/admin
```

The FastAPI application import and route registration were also verified. The current workspace no longer contains the earlier backend test files, so `pytest` currently reports `no tests ran`; behavioral regression tests should be restored before production deployment.

## Current launch limitations

This is a strong MVP, but the following work remains before a public production launch:

- Replace mock payment processing with a real payment provider and webhook verification.
- Add production PostgreSQL migration execution and backup procedures.
- Add rate limiting, audit logging, structured error tracking, and secret management.
- Add real venue images and richer venue detail content.
- Add owner availability blocking form directly to `/owner`.
- Add admin rejection, venue editing, and moderation notes.
- Add booking detail page and customer profile management.
- Restore automated backend integration tests.
- Add end-to-end browser tests for login, booking, approval, and cancellation.
- Add production deployment configuration, HTTPS, monitoring, and CI/CD.

## Recommended release checklist

1. Restore and run backend integration tests.
2. Configure production secrets and PostgreSQL.
3. Replace demo accounts and mock payment behavior.
4. Run `npm run typecheck` and `npm run build`.
5. Verify all role workflows in staging.
6. Confirm CORS, HTTPS, backups, logging, and rollback procedures.
7. Deploy the frontend and API separately or through the provided Compose baseline.
