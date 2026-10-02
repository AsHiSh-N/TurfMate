# TurfMate - Current System & Implementation Documentation

**Source-of-truth scope:** Updated for the Phase 1 stabilization on 2026-10-02. This document records the implementation and verification evidence currently present in the repository; historical audit text below has been reconciled to the current code.

Status labels: **IMPLEMENTED**, **PARTIALLY IMPLEMENTED**, **MOCK/PLACEHOLDER**, **NOT IMPLEMENTED**, and **IMPLEMENTED WITH KNOWN ISSUE**.

## 1. Executive Summary

TurfMate is a small sports venue discovery and booking MVP. The customer can search active venues by city and activity, request a generated availability grid, select a slot, and submit a booking while signed in. Venue owners can submit a venue with one court and view their venues. Administrators can list venues and approve them. Customers can list and cancel their own bookings. Payments are recorded as mock paid payments.

Current user types are `CUSTOMER`, `VENUE_OWNER`, and `ADMIN`. The role enum and API checks are present in the backend. The frontend has five routes: `/`, `/login`, `/bookings`, `/owner`, and `/admin`.

- **Implemented:** Next.js screens, FastAPI routes, SQLAlchemy persistence, JWT login, password hashing, venue submission/approval, booking-aware availability, schedule and ownership validation, booking/cancellation, SQLite booking serialization, mock payment records, API error states, backend regressions, and Playwright customer booking/cancellation plus error-state tests.
- **Partially implemented:** Owner/admin screens, owner block API, E2E role coverage, and deployment validation. Docker CLI is unavailable here; privileged owner/admin E2E workflows are not covered.
- **Mock/placeholder:** Payments are mock `PAID` rows; booking amount is fixed at 400; operating hours are fixed at 06:00–23:00; distance and seed data are demo-only.
- **Not implemented:** Real payment/refund gateway, venue detail page, profile management, venue/court editing, pricing/hour configuration UI, admin user management, active schema migrations, and production deployment/security controls.

This is an MVP suitable for local demonstration and further development, not a production-ready booking or payment service.

## 2. Product Overview

The current customer flow is:

```text
Open / → search city/activity → view active venue cards → request a date's hourly slots
→ choose a slot → sign in if needed → submit booking → receive booking reference
```

Venue discovery is served from `GET /api/venues`; availability from `GET /api/venues/{venue_id}/availability`; and booking creation from `POST /api/bookings`. The booking response is the confirmation shown by the UI. The UI does not force navigation to login; the home page tells an unsigned customer to sign in and select a slot.

Owner flow: sign in → open `/owner` → submit venue and first court → venue is `PENDING`. The owner can list their venues. There is also a backend endpoint to block a slot, but no form on the owner screen calls it.

Admin flow: sign in → open `/admin` → list venues, bookings, and payments → approve a pending venue. There is no user-management UI or admin user list API implementation beyond what is shown in the route inventory (none is registered for users).

## 3. Technology Stack

| Layer | Technology actually present | Purpose / status |
|---|---|---|
| Frontend | Next.js 16.3.8 App Router, React 18, TypeScript | Five browser routes and client-side API calls |
| Backend | Python 3.13, FastAPI, Uvicorn | JSON HTTP API |
| Database/ORM | SQLAlchemy 2; SQLite configured by default; SQLite file is used by the checked-in local `.env` | Persistence. Compose declares a persistent SQLite volume. PostgreSQL is not currently the default runtime. |
| Validation/settings | Pydantic 2, `pydantic-settings`, `email-validator` | Request bodies, email validation, environment settings |
| Authentication | `python-jose` JWT; Passlib PBKDF2-SHA256 | Bearer access tokens and password hashing |
| Styling/UI | Handwritten global CSS in `frontend/app/globals.css` | Styling and responsive rules; no component/UI framework dependency is declared |
| Frontend HTTP | Browser `fetch` | Calls API base URL from `NEXT_PUBLIC_API_URL` |
| Backend HTTP | FastAPI/Starlette | Route handling, CORS middleware, request validation |
| Test tools | pytest, FastAPI `TestClient`, Playwright Test | Nine backend tests and three browser E2E flows |
| Containerization | Dockerfiles and `docker-compose.yml` exist | Compose YAML parsed with duplicate-key rejection; Docker runtime is blocked here because the `docker` CLI is unavailable |
| External services | None integrated | Payment is local mock persistence; no maps, messaging, email, analytics, or cloud storage integration |

Dependency versions are recorded in `backend/requirements.txt` and `frontend/package-lock.json` / `frontend/package.json`. The framework was upgraded to Next.js 16.3.8 and PostCSS 8.5.23 after the current audit reported critical/high advisories; the final `npm audit` reports zero vulnerabilities.

## 4. Repository / Project Structure

```text
TurfMate/
├── README.md
├── TURFMATE_CURRENT_IMPLEMENTATION.md
├── docker-compose.yml
├── docs/
│   └── RELEASE_GUIDE.md                 # Older guide; parts are stale
├── backend/
│   ├── .env                             # Local configuration; secret values omitted here
│   ├── .env.example
│   ├── turfmate_local.db              # Local runtime SQLite database, generated data
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── app/
│   │   ├── main.py                      # FastAPI construction, CORS, router registration, create_all
│   │   ├── core/
│   │   │   ├── config.py                # Pydantic settings
│   │   │   └── security.py              # JWT and password helpers
│   │   ├── db/
│   │   │   ├── base.py                  # Declarative SQLAlchemy base
│   │   │   └── session.py               # Engine/session dependency
│   │   ├── models/__init__.py           # All seven ORM model classes
│   │   ├── schemas/
│   │   │   ├── auth.py                  # Login/register input models
│   │   │   └── common.py                # Booking, venue, and block input models
│   │   └── api/
│   │       ├── auth/routes.py
│   │       ├── venues/routes.py
│   │       ├── bookings/routes.py
│   │       ├── owner/routes.py
│   │       └── admin/routes.py
│   ├── scripts/seed.py                  # Creates demo users/activity/venue/court
│   └── tests/
│       ├── conftest.py                  # In-memory SQLite fixtures
│       └── test_platform_smoke.py       # Nine API/regression tests
└── frontend/
    ├── .env.example                     # Public API URL
    ├── .env.local                       # Local frontend API URL
    ├── package.json / package-lock.json
    ├── tsconfig.json
    ├── next.config.js
    ├── Dockerfile / .dockerignore
        ├── components/PortalNav.tsx
        ├── lib/api.ts                       # Shared API error mapping
        ├── e2e/customer-booking.spec.ts     # Playwright customer and error-state flows
    └── app/
        ├── layout.tsx
        ├── globals.css
        ├── page.tsx                     # Customer discovery and booking dialog
        ├── login/page.tsx
        ├── bookings/page.tsx
        ├── owner/page.tsx
        └── admin/page.tsx
```

No separate repository, service, or middleware package is present. `backend/app/models/__init__.py` contains the ORM classes rather than one file per model. `frontend/lib/` and `frontend/app/components/` are not used by the current implementation; the shared navigation component is under `frontend/components/`.

## 5. Application Architecture

The backend is a compact FastAPI application. `main.py` imports route modules, creates tables with SQLAlchemy `Base.metadata.create_all`, applies CORS, and registers routers. Each route directly queries or mutates the SQLAlchemy session; a separate business-service/repository layer is not present.

```text
Browser
  |
  | Next.js pages + fetch (NEXT_PUBLIC_API_URL)
  v
FastAPI application (CORS, request validation)
  +--> auth routes --> password helper / JWT helper
  +--> venue routes --> SQLAlchemy session --> SQLite database
  +--> booking routes --> SQLAlchemy session --> bookings + mock payments
  +--> owner routes --> venue/court/blocked-slot records
  +--> admin routes --> venue/booking/payment records
```

**Frontend:** App Router pages are primarily client components. `PortalNav` renders route links. Login stores bearer token and role in `localStorage`.

**Backend/API:** Router prefixes are registered in `main.py`; the backend uses synchronous FastAPI handlers and synchronous SQLAlchemy ORM sessions.

**Database:** SQLAlchemy tables are created at API import/startup and by the seed script. There is no active Alembic migration directory or migration execution in the inspected source tree. SQLite is configured by default; the local `.env` points to a SQLite file. The Compose service config uses a SQLite path under a named volume.

**Authentication:** Login verifies a stored password hash and returns a JWT whose subject is the user ID. Protected APIs decode the bearer token and then query the account role where required.

**Authorization:** Booking endpoints require `CUSTOMER`, owner endpoints require `VENUE_OWNER`, and admin endpoints require `ADMIN`. The public venue availability endpoint checks that the venue exists, but does not require `ACTIVE`; booking creation does require an active venue.

**External integrations:** None. Mock payment is represented by a database record; there is no external payment call.

## 6. User Roles

### Customer

| Capability | Status | Current behavior |
|---|---|---|
| Accessible screens | **PARTIAL** | `/`, `/login`, `/bookings`; no route guard prevents direct navigation to other pages |
| Search active venues | **IMPLEMENTED** | City and activity filters are passed to the venue list API |
| View availability / select slot | **PARTIAL** | Generated one-hour slots; not backed by operating-hour or pricing-rule tables |
| Create booking | **PARTIAL** | Authenticated, active venue/court/activity validation; fixed amount; no transactional reservation lock |
| View/cancel own bookings | **IMPLEMENTED** | API scopes list and cancel to token user ID; cancellation updates status |
| Registration | **PARTIAL** | Registration API exists; there is no registration screen |
| Profile/account management | **NOT IMPLEMENTED** | No profile endpoint or UI |

### Venue Owner

| Capability | Status | Current behavior |
|---|---|---|
| Owner screen | **PARTIAL** | `/owner` submits venue and lists owned venues; status errors are shown as basic notices |
| Submit venue | **IMPLEMENTED** | Creates `PENDING` venue and one court; no duplicate slug handling beyond DB uniqueness |
| Edit/activate/deactivate venue | **NOT IMPLEMENTED** | No endpoint or UI |
| Add/edit courts | **PARTIAL** | Venue submission creates its first court; no independent court management |
| Configure price/operating hours | **NOT IMPLEMENTED** | No owner API or UI for those settings |
| Block availability | **PARTIAL** | Backend endpoint exists and checks venue ownership; no owner UI form |
| View bookings/revenue/analytics | **NOT IMPLEMENTED** | No owner bookings endpoint in current route files; no reporting |
| Owner profile | **NOT IMPLEMENTED** | No profile feature |

### Administrator

| Capability | Status | Current behavior |
|---|---|---|
| Admin screen | **PARTIAL** | `/admin` displays venue queue, aggregate counts from returned lists, booking and payment lists |
| List all venues | **IMPLEMENTED** | Role-protected API |
| Approve venue | **IMPLEMENTED** | Sets venue status to `ACTIVE`; does not require current status to be `PENDING` |
| User/owner management | **NOT IMPLEMENTED** | No current admin user-list route or screen functionality |
| Booking/payment oversight | **IMPLEMENTED** | Read-only list endpoints; no refund or booking intervention |
| Reject/edit venue/configure platform | **NOT IMPLEMENTED** | No endpoints or UI |
| Admin profile/settings | **NOT IMPLEMENTED** | No feature |

## 7. Customer Application

### Home / Discovery

- **Route:** `/`
- **Purpose:** Search active venue cards and begin a booking.
- **UI:** `PortalNav`, city text input, fixed sport options (`All sports`, `Badminton`, `Cricket`), venue cards, modal with date input and slot buttons.
- **Data:** Venue ID, name, city, activity name/ID, rating, fixed starting price, fixed distance. Card does not render a venue image.
- **APIs:** `GET /api/venues?city=...&activity=...`; `GET /api/venues/{venue_id}/availability?date=...`; `POST /api/bookings`.
- **Actions:** Search, open a venue's availability, select a slot, submit a booking using a locally stored JWT.
- **Navigation:** `PortalNav` links to Discover, Bookings, and Sign in. Owner/admin links only appear if role prop is passed, but the shared nav uses are not consistently role-aware.
- **Validation/errors:** Displays a basic notice for missing token/slot or a failed booking response. Venue-list and availability fetch exceptions are not comprehensively handled. The client booking request relies on the backend to validate the selected slot.
- **Status:** **PARTIALLY IMPLEMENTED.** No separate venue details route/page; no images, maps, sorting, pagination, location-distance calculation, or real price data. UI offers Cricket although seed only creates Badminton. Changing date calls the availability loader in a way that can use the prior React state value.

### City search and sport filter

- **Route:** Embedded in `/`.
- **API:** Venue list query parameters `city` and `activity`.
- **Status:** **PARTIALLY IMPLEMENTED.** City equality is case-insensitive; activity is matched against the associated court activity slug. Filter option list is hardcoded, not loaded from `/api/activities`.

### Venue details

- **Route:** No dedicated venue detail route.
- **Status:** **NOT IMPLEMENTED.** The card opens an availability modal. No `GET /api/venues/{venue_id}` endpoint exists in current route file.

### Court/date/slot selection

- **Route:** Modal on `/`.
- **APIs:** `GET /api/venues/{venue_id}/availability?date=YYYY-MM-DD`.
- **Status:** **PARTIALLY IMPLEMENTED.** Court names and hourly slots are shown. Date format is browser native. Slots run 06:00–23:00 in fixed one-hour increments. Price is always 400. No stored slots, operating hours, or per-slot pricing are consulted.

### Booking and confirmation

- **Route:** Booking modal on `/`.
- **API:** `POST /api/bookings`.
- **Status:** **PARTIALLY IMPLEMENTED / MOCK PAYMENT.** Response reference and fixed total are shown as notice. No separate confirmation screen or receipt. See Booking Flow section.

### Login

- **Route:** `/login`.
- **API:** `POST /api/auth/login`.
- **UI/actions:** Email/password fields; demo customer credentials are prefilled in the form (credential values are intentionally not reproduced in this document). Successful login stores token and role in `localStorage`, then redirects by role.
- **Status:** **IMPLEMENTED WITH KNOWN ISSUE.** No logout action/session expiry UX; localStorage token is not centrally refreshed or cleared on API 401. No registration form.

### My bookings

- **Route:** `/bookings`.
- **APIs:** `GET /api/bookings`, `POST /api/bookings/{booking_id}/cancel`.
- **UI/data:** Booking reference, venue ID, date, times, total, status; cancellation button for `CONFIRMED` entries.
- **Status:** **PARTIALLY IMPLEMENTED.** No booking/venue detail navigation; cancel errors are not surfaced robustly; API is user-scoped.

### Profile/account

- **Route/API:** None.
- **Status:** **NOT IMPLEMENTED.**

## 8. Venue Owner Application

- **Owner screen:** `/owner`; page has a venue submission form and a list/status display. It reads/writes using the JWT in `localStorage`.
- **Venue submission:** `POST /api/owner/venues`; creates the venue in `PENDING` and its first `Court`. Owner list is `GET /api/owner/venues`.
- **Venue editing and activation:** **NOT IMPLEMENTED.**
- **Court management:** **PARTIALLY IMPLEMENTED.** First court is created as part of venue creation; no court update/delete/add endpoints.
- **Pricing:** **NOT IMPLEMENTED.** Price is hardcoded in availability and booking code. `PricingRule` model/table does not exist in the current model set.
- **Operating hours:** **NOT IMPLEMENTED.** Slot generation ignores configurable hours. No operating-hour model/table exists in current model file.
- **Availability blocking:** **PARTIALLY IMPLEMENTED.** `POST /api/owner/availability/block` validates owner role and ownership, then stores a `BlockedSlot`. No screen currently exposes the form. Blocked slots are used by availability generation.
- **Booking management/revenue/analytics/profile:** **NOT IMPLEMENTED.**

## 9. Admin Application

- **Route:** `/admin`.
- **Dashboard:** **PARTIALLY IMPLEMENTED.** Counts are derived from loaded venue, booking, and payment arrays; they are not database aggregate queries and there are no charts.
- **Venue review:** **IMPLEMENTED.** `GET /api/admin/venues`, then `POST /api/admin/venues/{venue_id}/approve`. No rejection path, moderation notes, or edit action.
- **Booking oversight:** **IMPLEMENTED, read-only.** `GET /api/admin/bookings`.
- **Payment oversight:** **IMPLEMENTED, read-only.** `GET /api/admin/payments`.
- **User/owner management, courts, configuration, system settings:** **NOT IMPLEMENTED.**
- API authorization validates a token subject and confirms the database user has the `ADMIN` role.

## 10. Venue / Court / Slot Model

The implemented database relationship is:

```text
User (owner)
  └── Venue (owner_id)
        └── Court (venue_id, activity_id)
              ├── Booking (court_id, venue_id, activity_id)
              └── BlockedSlot (court_id, date, interval)
Activity
  ├── Court (activity_id)
  └── Booking (activity_id)
User (customer)
  └── Booking (user_id)
Booking
  └── Payment (booking_id)
```

The ORM declares foreign keys but no explicit SQLAlchemy `relationship()` properties. There is no City table: city is a string on Venue. There is no persisted Sport-specific join table: a Court has one `activity_id`. There is no Slot table: slots are computed for a requested date. Booking and blocked intervals hold dates and times.

### Current model fields

| Model/table | Fields in current ORM | Keys/constraints |
|---|---|---|
| `users` / `User` | `id`, `name`, `email`, `phone`, `password_hash`, `role` | PK `id`; unique `email`; role enum `CUSTOMER`, `VENUE_OWNER`, `ADMIN` |
| `activities` / `Activity` | `id`, `name`, `slug` | PK `id`; unique `slug` |
| `venues` / `Venue` | `id`, `owner_id`, `name`, `slug`, `description`, `address`, `city`, `state`, `pincode`, `status`, `rating` | PK; FK `owner_id -> users.id`; unique `slug`; status enum `PENDING`, `ACTIVE`, `REJECTED` |
| `courts` / `Court` | `id`, `venue_id`, `activity_id`, `name` | PK; FKs `venue_id -> venues.id`, `activity_id -> activities.id` |
| `bookings` / `Booking` | `id`, `booking_reference`, `user_id`, `venue_id`, `court_id`, `activity_id`, `booking_date`, `start_time`, `end_time`, `total_amount`, `status` | PK; unique `booking_reference`; FKs to user, venue, court, activity; status `CONFIRMED`, `CANCELLED` |
| `payments` / `Payment` | `id`, `booking_id`, `transaction_id`, `amount`, `status` | PK; FK `booking_id -> bookings.id`; unique `transaction_id`; status is plain string, default `PAID` |
| `blocked_slots` / `BlockedSlot` | `id`, `court_id`, `date`, `start_time`, `end_time`, `reason`, `status` | PK; FK `court_id -> courts.id`; status is plain string, default `ACTIVE` |

Declared mapped types are integer, strings, date/time, float, and SQLAlchemy enums. No additional secondary indexes, check constraints, unique court names, or composite booking constraints are declared in this current model file. Primary-key and unique constraints are database constraints.

### Slot availability logic

`slots_for_day()` in `backend/app/core/booking_rules.py` defines one-hour intervals from 06:00 to 23:00. Availability is served only for active venues and marks elapsed slots, overlapping active blocks, and overlapping `CONFIRMED` bookings unavailable. `CANCELLED` bookings do not block availability. Hours are fixed MVP rules, not stored venue schedules.

### Pricing logic

The availability response returns `price: 400`; booking creation sets `total_amount=400`. There is no pricing computation, tax, fee, discount, currency, or persisted price configuration in the current model set.

## 11. Booking Flow

```text
Customer selects venue and date
        ↓
GET availability generates fixed hourly slots
        ↓
Customer selects court/slot in the browser
        ↓
POST /api/bookings with bearer JWT
        ↓
Backend checks CUSTOMER role, future time, exact one-hour schedule, active venue, court/activity association
        ↓
SQLite BEGIN IMMEDIATE; backend checks blocks and overlapping CONFIRMED booking rows
        ↓
Booking is saved as CONFIRMED with total 400
        ↓
A Payment row is saved as PAID with MOCK transaction ID
        ↓
API returns booking reference and UI displays it
```

- **Availability:** Active venues only; generated slots account for elapsed time, blocked intervals, and existing confirmed bookings. Cancelled bookings release availability.
- **Duplicate/concurrent booking prevention:** SQLite `BEGIN IMMEDIATE` serializes the conflict check and booking write. A file-backed regression test confirms one success and one HTTP 409 for two simultaneous requests. This is database-wide writer serialization; other database dialects have no equivalent lock or interval constraint.
- **Booking status:** Only `CONFIRMED` and `CANCELLED` enums exist. There is no pending/expired/completed lifecycle.
- **Cancellation:** A customer can cancel only a booking with matching `user_id`; it sets status to `CANCELLED` and returns 409 on repeat. The mock payment stays `PAID`; no refund is implemented.
- **Payment status:** Mock `Payment` row status defaults to `PAID`. Booking API response hardcodes `payment_status: PAID`; there is no payment provider or webhook.
- **Pricing:** Fixed at 400 regardless of venue, court, or time.
- **Confirmation:** A unique-looking `SPT-YYYYMMDD-<random>` reference is created, but no dedicated confirmation view/email is sent.
- **Date validation:** Past dates and elapsed start times are rejected; time interpretation remains server-local.

## 12. Authentication & Authorization

- Login: `POST /api/auth/login` accepts a validated email and password, finds the user by normalized email, verifies PBKDF2-SHA256 hash, and returns an access token, token type, role, and name.
- Registration: `POST /api/auth/register` creates a `CUSTOMER` user and returns the same token shape. It has no password length or name/phone constraints beyond basic types in the current Pydantic model.
- Session/token: JWT HS256 by default (configured algorithm); token subject is user ID and expiry uses `ACCESS_TOKEN_EXPIRE_MINUTES`. The frontend stores token and role in `localStorage` under `turfmate_token` and `turfmate_role`.
- Protected API: `HTTPBearer` requires an Authorization bearer token. `get_current_user` decodes it; invalid/expired tokens return 401.
- Role checks: booking routes require a customer account; owner routes require venue owner; admin routes require admin. Owner venue/slot operations also scope requested venues to the owner ID. Customer booking list/cancel is scoped to the token user.
- Frontend route protection: **NOT IMPLEMENTED.** Pages are not protected by middleware/layout checks; API rejects unauthorized requests. Login redirects based on the returned role.
- Logout: No server-side token revocation or frontend logout control is implemented.
- Secrets: A JWT secret is configured locally and in the example configuration. Values are not reproduced here. Default config also contains a development fallback; this is unsuitable for deployment.

## 13. API Documentation

All routes are under the FastAPI OpenAPI docs at `/docs` when the backend is running.

| Method | Endpoint | Purpose | Auth | Role |
|---|---|---|---|---|
| `GET` | `/health` | Health response | No | Public |
| `POST` | `/api/auth/login` | Verify credentials and return JWT/role/name | No | Any existing role |
| `POST` | `/api/auth/register` | Create customer and return JWT | No | Public; always creates customer |
| `GET` | `/api/activities` | List all activity records | No | Public |
| `GET` | `/api/venues` | List active venues; optional city/activity filters | No | Public |
| `GET` | `/api/venues/{venue_id}/availability` | Generate date slots for each venue court | No | Public |
| `POST` | `/api/bookings` | Validate and create booking plus mock payment | Bearer | Customer |
| `GET` | `/api/bookings` | List current customer's bookings | Bearer | Customer |
| `POST` | `/api/bookings/{booking_id}/cancel` | Cancel current customer's booking | Bearer | Customer |
| `GET` | `/api/owner/venues` | List venues owned by current user | Bearer | Venue owner |
| `POST` | `/api/owner/venues` | Create pending venue and initial court | Bearer | Venue owner |
| `POST` | `/api/owner/availability/block` | Block an owned venue court interval | Bearer | Venue owner |
| `GET` | `/api/admin/venues` | List all venues | Bearer | Admin |
| `POST` | `/api/admin/venues/{venue_id}/approve` | Set venue status to active | Bearer | Admin |
| `GET` | `/api/admin/bookings` | List booking summaries | Bearer | Admin |
| `GET` | `/api/admin/payments` | List payment summaries | Bearer | Admin |

No standalone user, court, venue-detail, operating-hour, pricing, review, or owner-booking endpoint is registered. The `GET /api/venues/{venue_id}/availability` endpoint requires a `date` query parameter parsed as ISO date. API request bodies are `LoginRequest`, `RegisterRequest`, `BookingCreate`, `VenueCreate`, and `BlockCreate` from `backend/app/schemas/`.

## 14. Database Documentation

The seven tables are defined in `backend/app/models/__init__.py`. See the table in Section 10 for fields, types, keys, and foreign keys. The model code declares no explicit ORM relationships. Tables are created by `Base.metadata.create_all(bind=engine)` in `backend/app/main.py` and `seed.py`.

```text
users 1 ── * venues       (owner_id)
users 1 ── * bookings     (user_id)
venues 1 ── * courts      (venue_id)
venues 1 ── * bookings    (venue_id)
activities 1 ── * courts  (activity_id)
activities 1 ── * bookings(activity_id)
courts 1 ── * bookings    (court_id)
courts 1 ── * blocked_slots(court_id)
bookings 1 ── * payments  (booking_id; schema does not enforce one payment only)
```

No City, operating-hours, pricing-rule, image, review, or persistent slot table exists in the current ORM declaration. No migration revision is present in the current repository inventory. Existing SQLite files created under a prior schema may not be upgraded by `create_all`; it creates missing tables but does not alter existing table layouts.

## 15. Business Logic

| Rule | Current implementation |
|---|---|
| New venue starts pending | `owner/routes.py` sets `VenueState.PENDING` |
| Public venue discovery lists active venues | `venues/routes.py` filters `VenueState.ACTIVE` |
| Admin approval activates venue | `admin/routes.py` sets status to `ACTIVE` |
| Owner can only manage own venue | Owner role plus `owner_id` query filter in `owner/routes.py` |
| Activity associated to a venue | Current creation adds a Court with the activity ID; venue list derives activity from the first court |
| Generated opening hours | Fixed 06:00–23:00 in `slots_for`; not configurable |
| Slot duration | Fixed at one hour |
| Block interval makes slot unavailable | Overlap comparison against active blocked slots in `venues/routes.py` |
| Booking must use active venue and matching court/activity | Checks in `bookings/routes.py` |
| End must be after start | Booking requires exact one-hour schedule slots; block API validates a positive interval within 06:00–23:00 |
| Confirmed booking overlap is rejected | SQLite immediate transaction checks same court/date interval overlap; HTTP 409 |
| Booking price/payment | Backend-owned fixed total 400 and local `MOCK-` payment row with `PAID` status |
| Customer can only access own bookings | user ID filter in list and cancel routes |

## 16. Frontend Components

| Component/screen | Location | Purpose/status |
|---|---|---|
| Root layout | `frontend/app/layout.tsx` | HTML wrapper, global CSS, metadata |
| `PortalNav` | `frontend/components/PortalNav.tsx` | Brand and route links; role-specific links only when role prop is passed |
| Discovery/booking | `frontend/app/page.tsx` | City/sport search, venue cards, availability modal, slot selection, booking request |
| Login | `frontend/app/login/page.tsx` | Email/password login, localStorage token storage, role redirect |
| Bookings | `frontend/app/bookings/page.tsx` | Customer list and cancellation action |
| Owner | `frontend/app/owner/page.tsx` | Venue submission and owner venue list; no block slot form |
| Admin | `frontend/app/admin/page.tsx` | Venue approval plus booking/payment lists and counts |
| Global styles | `frontend/app/globals.css` | Shared nav, shell, cards, modal, grid, responsive rules |
| Venue card/filter/slot selector | Inline in `app/page.tsx` | Not extracted as reusable components |
| Data tables/charts | None | Lists are rendered as inline cards; no chart library |

The frontend uses a small shared API helper for response parsing/error mapping; it does not have an auth context, component library, or form-validation library.

## 17. Backend Components

| Module | Responsibility |
|---|---|
| `backend/app/main.py` | Construct FastAPI app, CORS, metadata table creation, router registration, `/health` |
| `backend/app/api/auth/routes.py` | Login and customer registration |
| `backend/app/api/venues/routes.py` | Activities, active venue search, date availability and slot generation |
| `backend/app/api/bookings/routes.py` | Customer booking, overlap query, mock payment row, customer list/cancel |
| `backend/app/api/owner/routes.py` | Owner-role validation, venue creation/listing, blocked intervals |
| `backend/app/api/admin/routes.py` | Admin-role validation, venue list/approval, booking/payment lists |
| `backend/app/core/security.py` | Password hashing/verification, JWT encode/decode, bearer dependency |
| `backend/app/core/booking_rules.py` | Fixed hourly schedule, server-side price, slot validation |
| `backend/app/core/config.py` | Settings from environment and optional `.env` |
| `backend/app/db/session.py` | SQLAlchemy engine, session factory and `get_db` dependency |
| `backend/app/db/base.py` | Declarative model base |
| `backend/app/models/__init__.py` | All ORM model and enum declarations |
| `backend/app/schemas/` | Pydantic input models |
| `backend/scripts/seed.py` | Demo database bootstrap and seed records |

No dedicated services/repositories packages contain implementation. Error handling mostly raises FastAPI `HTTPException`; unhandled database exceptions use framework defaults. CORS allows configured frontend URL and localhost 3000.

## 18. Environment Configuration

Values below are names/purposes only. Secret values are intentionally not included.

| Variable | Purpose | Required? | Example/default shape |
|---|---|---|---|
| `DATABASE_URL` | SQLAlchemy database URL | No in code; defaults to SQLite | `sqlite:///./turf.db` |
| `JWT_SECRET` | JWT signing key | No in code, but must be replaced for deployment | `SECRET PRESENT — VALUE REDACTED` |
| `JWT_ALGORITHM` | JWT signing algorithm | No; default `HS256` | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration | No; default 120 | `120` |
| `FRONTEND_URL` | CORS frontend origin | No; default localhost port 3000 | `http://localhost:3000` |
| `NEXT_PUBLIC_API_URL` | Frontend API base URL | No; default `http://localhost:8000/api` in pages | `http://localhost:8000/api` |

`backend/.env` exists and contains a configured JWT secret; its value is intentionally redacted. `backend/.env.example` uses a placeholder secret. The frontend local env file points at localhost API. Do not use demo or fallback secrets in production. The docs avoid reproducing seeded demo password values.

## 19. External Integrations

| Integration | Provider/method | Current status |
|---|---|---|
| Database | SQLAlchemy URL; local SQLite; Compose SQLite volume | Implemented for local persistence. No managed database service configured. |
| Payment | No provider; inserts a `Payment` row with generated `MOCK-...` transaction ID | **MOCK/PLACEHOLDER**; no gateway, authorization, capture, webhook, refund, or reconciliation |
| Maps/geocoding | None | Not implemented; distance is a constant response value |
| Email/SMS | None | Not implemented |
| File/image storage | None | Not implemented; venue has no image field in current schema |
| Analytics/monitoring | None | Not implemented |
| Identity provider | None | First-party password/JWT implementation |

## 20. Docker / Deployment

Current Docker-related files are `backend/Dockerfile`, `frontend/Dockerfile`, `.dockerignore` files, and root `docker-compose.yml`.

Compose declares:

- `backend`: builds Python image, points SQLite to `/data/turf.db`, mounts named volume `turf_data`, publishes host port 8000, and has a health check against `/health`.
- `frontend`: builds Next.js image and publishes host port 3000; depends on backend health.
- Named volume `turf_data` persists the SQLite database. No explicit custom network is declared; Compose supplies its default network.

**Current status:** Compose YAML parses without duplicate keys and contains one frontend `args` mapping. Docker runtime validation is blocked in this environment because the `docker` CLI is not installed. The frontend API URL is set through the service environment and build arg; container startup remains unverified.

No Kubernetes, cloud deployment, reverse proxy, TLS, CI/CD, production profile, backup job, or migration service is present. The API creates tables at startup rather than running schema migrations.

Commands documented in README:

```bash
docker compose up --build
docker compose down
```

The Compose files exist, but successful Compose execution is **not confirmed** here.

## 21. Testing

- Framework: pytest.
- Test infrastructure: `backend/tests/conftest.py` creates an in-memory SQLite database with `StaticPool`, recreates metadata per test, and overrides `get_db` for FastAPI `TestClient`.
- Test file: `backend/tests/test_platform_smoke.py`.
- Covered behavior: owner venue creation, pending visibility, admin approval, active venue discovery, customer booking creation, mock paid response, customer booking listing, denial of admin access to a customer token, invalid login/token checks, duplicate booking rejection, repeat cancellation rejection, and seed/idempotence checks.
- Current observed result: `9 passed, 1 warning in 1.46s` (final full-suite rerun).
- Frontend: `npm run typecheck` and `npm run build` passed on Next.js 16.3.8. Playwright E2E covers customer login/discovery/availability/booking/history/cancellation, unauthenticated role-page feedback, and API-unavailable feedback.
- Coverage percentage: not configured or measured.
- Untested: registration UI, privileged owner/admin browser workflows, database upgrade behavior, Docker runtime startup, and cross-database concurrency.

## 22. Security

### Implemented

- PBKDF2-SHA256 password hashing via Passlib.
- JWT bearer authentication with expiry.
- Role checks in customer booking, owner, and admin APIs.
- Owner resource scoping and customer booking scoping.
- Pydantic request parsing and `EmailStr` validation for auth.
- SQLAlchemy ORM parameterized queries rather than concatenated SQL.
- CORS middleware configured for frontend origin(s).

### Missing / known gaps

- Development fallback JWT secret exists; no production secret validation/rotation mechanism.
- Demo accounts use a source-defined shared development password.
- No rate limiting, account lockout, email verification, password reset, MFA, audit trail, or token revocation.
- No explicit secure headers, CSRF defenses, or content security policy are configured. JWT is stored in browser localStorage, making it accessible to injected scripts if an XSS issue arises.
- Frontend routes are not protected; API role checks are the actual access boundary.
- Request schemas have limited business constraints (for example, password length, venue field validation, date not in past, block end after start).
- SQLite booking creation uses `BEGIN IMMEDIATE` during conflict-check plus write; this is database-wide serialization, not a portable interval constraint.
- `npm audit --audit-level=high` reports zero vulnerabilities after the Next.js/PostCSS update; repeat dependency audits before release.
- SQLite is suitable for local/demo use but no production database configuration, backup, or migration process is verified.

## 23. Error Handling

- **Frontend:** a shared API helper handles API outage, unauthorized, forbidden, validation, conflict, not-found, and server errors. Errors are displayed in route alert areas.
- **Authentication:** invalid credentials produce HTTP 401 `Invalid credentials`; missing credentials produce HTTP 401 `Authentication required`; invalid/expired bearer JWT produces HTTP 401 `Invalid or expired token`.
- **Authorization:** role mismatch produces HTTP 403 with role-specific messages such as `Customer access required`, `Venue owner access required`, or `Admin access required`.
- **Booking:** past/out-of-window slots return HTTP 400; unavailable/invalid venue, court, or activity association returns 404; active blocks and overlapping confirmed bookings return 409.
- **Venue/owner/admin:** missing activity/venue/court produce 404. Duplicate venue slug can surface as an unhandled database integrity error because there is no explicit duplicate check/translation in the current owner route.
- **Database/server:** no custom global exception handler or structured error logging is present; unexpected errors follow FastAPI/ASGI defaults.
- Availability takes a typed ISO date; malformed values are rejected by FastAPI with HTTP 422.

## 24. Current Limitations & Known Issues

| Area | Current state | Issue / impact |
|---|---|---|
| Compose config | Frontend build config present and readable | Docker runtime validation is blocked here because the `docker` CLI is unavailable |
| Docker | Dockerfiles exist | Docker unavailable in inspection environment; no claim of successful image startup |
| Payment | Mock only | No real payment or refund; booking is marked paid immediately |
| Pricing | Constant 400 | Displayed/charged total does not vary by venue or slot |
| Availability | Generated 06:00–23:00 hourly schedule | Hardcoded schedule and amount; active blocks, confirmed bookings, cancelled bookings, and elapsed slots are handled |
| Booking conflicts | Overlap query inside SQLite `BEGIN IMMEDIATE` transaction | Tested concurrent SQLite requests serialize; global writer contention and no non-SQLite interval constraint remain |
| Slot blocking | Validated owner API only | No owner form; validates interval/ownership and rejects overlap with confirmed bookings |
| Dates | Typed date values | Past dates/times are rejected; server-local timezone/business-day policy is not configurable |
| Activity choices | Hardcoded UI filter | Only Badminton is seeded; Cricket option may yield no records |
| Venue images/details | No image schema or detail route | Cards use a generated initial; there is no full detail view |
| Owner tools | Venue submission/list only | No edit, court maintenance, pricing, hours, bookings, revenue, or analytics |
| Admin tools | Approve and read-only lists | No rejection, user management, configuration, or moderation notes |
| Authentication UI | Login only | Register endpoint has no screen; no logout control/token revocation |
| Model evolution | `create_all` at import/startup | Does not alter existing tables; no migration revisions in current repo |
| Test quality | Nine backend API/regression tests plus three Playwright E2E flows | No coverage percentage; owner/admin privileged browser paths and DB migration behavior remain untested |
| Frontend errors | Shared API error helper and visible alerts | No field-level error mapping for every form validation response |
| Documentation | `docs/RELEASE_GUIDE.md` | Contains stale claims, including prior scope/test and feature statements; this file is current source-based reference |
| Secrets | Local `.env` present | Secret value must remain out of docs and must be replaced/managed for deployment |

Source search in application code found mock payment behavior and the `Base` class `pass`; no application TODO/FIXME marker was found in the inspected source directories. Generated `.next` and `node_modules` contain third-party TODO text and are not application TODOs.

## 25. Implementation Status Matrix

| Module | Feature | Status | Notes |
|---|---|---|---|
| Customer | Venue discovery | ✅ IMPLEMENTED | Active venue list with city/activity filters |
| Customer | Venue details | ❌ NOT IMPLEMENTED | No detail endpoint/page |
| Customer | Slot availability | ✅ IMPLEMENTED WITH MVP LIMITS | Active venue, elapsed time, confirmed booking and block state handled; schedule is fixed |
| Customer | Booking | ✅ IMPLEMENTED WITH MVP LIMITS | Server validates selected slot, ownership relationships, conflicts, and fixed price; SQLite lock is database-wide |
| Customer | Booking history/cancel | ✅ IMPLEMENTED | Own-booking scope; basic UI |
| Customer | Profile/registration UI | ❌ NOT IMPLEMENTED | Register API exists, no UI; no profile APIs |
| Owner | Venue management | 🟡 PARTIALLY IMPLEMENTED | Create pending/list; no edit/status controls |
| Owner | Court management | 🟡 PARTIALLY IMPLEMENTED | Initial court only |
| Owner | Availability block | 🟡 PARTIALLY IMPLEMENTED | Validated ownership-scoped API, no portal form |
| Owner | Booking/revenue management | ❌ NOT IMPLEMENTED | No route/screen |
| Admin | Dashboard | 🟡 PARTIALLY IMPLEMENTED | Counts from list payloads |
| Admin | User management | ❌ NOT IMPLEMENTED | No user API/screen |
| Admin | Venue approval | ✅ IMPLEMENTED | Role-protected activation |
| Admin | Booking/payment lists | ✅ IMPLEMENTED | Read-only API and screen |
| Authentication | Login/JWT | ✅ IMPLEMENTED | LocalStorage browser token |
| Authorization | Role checks | ✅ IMPLEMENTED | Enforced in protected APIs |
| Payment | Gateway | 🟠 MOCK / PLACEHOLDER | Inserts a mock `PAID` payment row |
| Database | Local persistence | ✅ IMPLEMENTED | SQLite + `create_all`; no migrations |
| Deployment | Docker Compose | ⚠️ PARTIALLY VERIFIED | Compose file is in place, but Docker runtime execution is blocked in this environment |
| Tests | Backend and browser integration | 🟡 PARTIALLY IMPLEMENTED | Nine pytest tests and three Playwright flows; privileged owner/admin E2E absent |

## 26. Current User Journeys

### Customer

```text
Open / → search city/activity → choose active venue → load availability
→ choose slot → authenticate if token absent → POST booking → show reference
→ /bookings to view/cancel
```

The current core customer journey is exercised by Playwright against an isolated seeded SQLite database. Availability reflects confirmed bookings, blocks, cancellations, and elapsed slots. No real payment occurs.

### Owner

```text
Sign in → /owner → submit venue and first court → venue is PENDING → view own venue list
```

Implemented with API role checks. The journey does not include configuring schedule/prices, managing more courts, viewing bookings, or blocking slots from the owner UI. An API-only block endpoint exists.

### Admin

```text
Sign in → /admin → review venue list → approve pending venue → venue becomes ACTIVE
→ inspect booking/payment lists
```

Implemented for approval and read-only lists. No user-management or rejection journey exists.

## 27. Current Product Scope

### Working today

- Browse seeded active venues by city and activity.
- Load one-hour availability grid for a date.
- Sign in and register through API (registration UI absent).
- Submit a venue and initial court as owner.
- Approve a venue as admin.
- Create/cancel customer bookings with a fixed mock payment record.
- List current user's bookings and admin booking/payment summaries.
- Block an owner venue interval through the API.

### Partially working

- Schedule and price are fixed MVP constants; owner/admin pages remain limited in capability.
- Owner/admin web pages (limited feature coverage).
- Authentication UX (no route protection/logout/register page).
- Local/Docker setup (manual SQLite path is available; Docker runtime validation is blocked in this environment because the Docker CLI is unavailable).

### Not yet built

- Real payments, refunds, webhooks.
- Venue details/images/maps, dynamic rating/distance.
- Configurable operating hours, stored slots, and dynamic pricing.
- Owner booking/revenue tools, court edit management, owner availability blocking form.
- Admin user management, rejection workflow, configuration.
- Customer profile/password recovery.
- Production migrations, deployment infrastructure, observability, CI/CD, backups.

## 28. Recommended Next Implementation Steps

These are technical backlog items derived from present gaps, not claims of existing features.

| Priority | Area | Task | Reason |
|---|---|---|---|
| P0 | Local/deploy config | Validate Docker Compose in an environment with Docker installed | Current environment cannot run Docker, so container startup remains unverified here |
| P0 | Booking correctness | Add a database-specific interval exclusion constraint if moving beyond local SQLite | Current SQLite transaction serializes writers database-wide; other dialects lack an equivalent lock |
| P0 | Schema evolution | Add and test migrations for all current models; remove startup-only schema assumptions before upgrades | `create_all` does not migrate existing tables |
| P1 | Validation/security | Add interval/date/field constraints and consistent error handling; validate block end > start and block overlap with bookings | Current requests can represent invalid business cases |
| P1 | Owner portal | Add owner UI for blocking and listing venue courts; align inputs with real activity IDs | Existing endpoint is not reachable through owner screen; form hardcodes activity ID |
| P1 | Availability/pricing | Decide and implement data-backed schedules, pricing, and booking-aware availability | Current schedule and price are constants |
| P1 | Tests | Extend privileged owner/admin browser coverage and migration tests | Current nine API tests and three Playwright journeys focus on customer flow and access denial |
| P2 | Auth UX | Add registration/logout/token-expiry handling and route UX for unauthenticated roles | API registration exists but not a screen; token persists in localStorage |
| P2 | Admin | Add explicit user/owner API only if required by existing scope; test approval state transitions | Current console lacks user management and rejection |
| P2 | Dependencies | Continue scheduled dependency review and audits | Current `npm audit` reports zero vulnerabilities after the framework update |
| P3 | Operational readiness | Add production secrets, database, deployment/HTTPS, monitoring, and backup configuration | No production deployment setup currently exists |

## 29. Appendix

### Frontend routes

```text
/          discovery, availability modal, booking submit
/login     login
/bookings  own bookings and cancel
/owner     submit/list venues
/admin     venue approval and read-only operations lists
```

### API endpoints

```text
GET    /health
POST   /api/auth/login
POST   /api/auth/register
GET    /api/activities
GET    /api/venues
GET    /api/venues/{venue_id}/availability?date=YYYY-MM-DD
POST   /api/bookings
GET    /api/bookings
POST   /api/bookings/{booking_id}/cancel
GET    /api/owner/venues
POST   /api/owner/venues
POST   /api/owner/availability/block
GET    /api/admin/venues
POST   /api/admin/venues/{venue_id}/approve
GET    /api/admin/bookings
GET    /api/admin/payments
```

### Database models

```text
User, Activity, Venue, Court, Booking, Payment, BlockedSlot
```

### Environment variable names

```text
DATABASE_URL
JWT_SECRET
JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES
FRONTEND_URL
NEXT_PUBLIC_API_URL
```

### Local commands

From repository root, backend terminal:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m scripts.seed
uvicorn app.main:app --reload
```

Frontend terminal:

```bash
cd frontend
npm ci
cp .env.example .env.local
npm run dev
```

### Build/test commands

```bash
cd frontend
npm run typecheck
npm run build

cd ../backend
python -m pytest -q
```

### Docker commands and ports

```bash
docker compose up --build
docker compose down
```

Intended host ports are 3000 (frontend) and 8000 (API). Compose YAML was parsed with duplicate-key checking and is valid; Docker execution, image build, and container startup were not performed because the Docker CLI is unavailable.

### Important configuration/source files

```text
backend/app/main.py
backend/app/core/config.py
backend/app/core/security.py
backend/app/db/session.py
backend/app/models/__init__.py
backend/app/api/*/routes.py
backend/app/schemas/*.py
backend/scripts/seed.py
backend/requirements.txt
backend/.env.example
frontend/package.json
frontend/next.config.js
frontend/tsconfig.json
frontend/.env.example
frontend/Dockerfile
docker-compose.yml
```
