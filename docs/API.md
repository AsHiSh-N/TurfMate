# API Inventory

This inventory reflects the actual HTTP routes registered in the current FastAPI application.

## Authentication

| Method | Endpoint | Purpose | Auth | Role | Status |
|---|---|---|---|---|---|
| POST | `/api/auth/login` | Sign in and receive JWT | No | Any | IMPLEMENTED |
| POST | `/api/auth/register` | Register a customer user | No | Any | IMPLEMENTED |

## Public discovery

| Method | Endpoint | Purpose | Auth | Role | Status |
|---|---|---|---|---|---|
| GET | `/health` | Health check | No | Any | IMPLEMENTED |
| GET | `/api/activities` | List activities | No | Any | IMPLEMENTED |
| GET | `/api/venues` | List active venues with optional city/activity filters | No | Any | IMPLEMENTED |
| GET | `/api/venues/{venue_id}/availability` | Generate availability for each court of an active venue | No | Any | IMPLEMENTED |

## Customer booking

| Method | Endpoint | Purpose | Auth | Role | Status |
|---|---|---|---|---|---|
| POST | `/api/bookings` | Create a validated one-hour booking with fixed server-side mock pricing | Yes | CUSTOMER | IMPLEMENTED |
| GET | `/api/bookings` | List a customer’s bookings | Yes | CUSTOMER | IMPLEMENTED |
| POST | `/api/bookings/{booking_id}/cancel` | Cancel a customer booking | Yes | CUSTOMER | IMPLEMENTED |

## Owner

| Method | Endpoint | Purpose | Auth | Role | Status |
|---|---|---|---|---|---|
| GET | `/api/owner/venues` | List owner venues | Yes | VENUE_OWNER | IMPLEMENTED |
| POST | `/api/owner/venues` | Create venue and first court | Yes | VENUE_OWNER | IMPLEMENTED |
| POST | `/api/owner/availability/block` | Block an unbooked interval on an owned venue court | Yes | VENUE_OWNER | API IMPLEMENTED; no UI |

## Admin

| Method | Endpoint | Purpose | Auth | Role | Status |
|---|---|---|---|---|---|
| GET | `/api/admin/venues` | List all venues | Yes | ADMIN | IMPLEMENTED |
| POST | `/api/admin/venues/{venue_id}/approve` | Approve venue | Yes | ADMIN | IMPLEMENTED |
| GET | `/api/admin/bookings` | List all bookings | Yes | ADMIN | IMPLEMENTED |
| GET | `/api/admin/payments` | List all payment records | Yes | ADMIN | IMPLEMENTED |

## API observations

- The frontend calls the API with browser `fetch` requests and stores the bearer token in local storage.
- There is no dedicated venue details endpoint or profile endpoint in the current backend.
- There is no API consumer currently using `/api/activities` in the frontend; the UI uses a hardcoded sport selector instead.
- The `owner availability block` route exists but is not wired to a working UI form.
- The route implementations are direct and use SQLAlchemy queries in the route body rather than a service layer.

## Booking and availability contract

- Availability accepts an ISO date. Invalid dates return 422; unknown or non-active venues return 404.
- Generated slots are local-time one-hour intervals with starts from 06:00 through 22:00 and closing at 23:00. Elapsed slots, active blocked intervals, and overlapping `CONFIRMED` bookings are returned with `available: false`; `CANCELLED` bookings do not block a slot.
- Booking creation ignores frontend-supplied identity or price fields. It requires a future date/time and an exact one-hour interval in the generated window, an active venue, and a court attached to both the venue and selected activity.
- A blocked or already-confirmed overlapping interval returns 409. Invalid/past/out-of-window slots return 400. Missing/expired bearer tokens return 401; role mismatch returns 403.
- Booking amount is fixed at 400 on the server. The associated `MOCK-...` payment is recorded as `PAID`; cancellation changes only booking status and does not imply a refund.
- Owner block requests must have a positive interval within 06:00–23:00, belong to the owner, and not overlap a confirmed booking.

## API status summary

- Implemented endpoints: 16 total across health, auth, discovery, booking, owner, and admin
- Owner block endpoint is implemented and validated but remains API-only; there is no owner blocking form
- Mismatch note: frontend has a booking UI and a login UI, but no registration UI despite `POST /api/auth/register` being implemented
