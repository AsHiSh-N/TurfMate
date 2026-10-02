# Database Inventory

## Current database technology

The current runtime default is SQLite. The config in `backend/app/core/config.py` sets `DATABASE_URL` to `sqlite:///./turf.db`, and the working local environment uses `backend/turfmate_local.db`.

## ORM model inventory

The actual models are defined in `backend/app/models/__init__.py`.

### User
- Table: `users`
- Key fields: `id`, `name`, `email`, `phone`, `password_hash`, `role`
- Constraints: `email` is unique; `role` is an enum of `CUSTOMER`, `VENUE_OWNER`, `ADMIN`

### Activity
- Table: `activities`
- Key fields: `id`, `name`, `slug`
- Constraints: `slug` is unique

### Venue
- Table: `venues`
- Key fields: `id`, `owner_id`, `name`, `slug`, `description`, `address`, `city`, `state`, `pincode`, `status`, `rating`
- Constraints: `slug` is unique; `owner_id` references `users.id`; `status` is enum of `PENDING`, `ACTIVE`, `REJECTED`

### Court
- Table: `courts`
- Key fields: `id`, `venue_id`, `activity_id`, `name`
- Constraints: `venue_id` references `venues.id`; `activity_id` references `activities.id`

### Booking
- Table: `bookings`
- Key fields: `id`, `booking_reference`, `user_id`, `venue_id`, `court_id`, `activity_id`, `booking_date`, `start_time`, `end_time`, `total_amount`, `status`
- Constraints: `booking_reference` is unique; `user_id`, `venue_id`, `court_id`, `activity_id` all reference parent tables; `status` is enum of `CONFIRMED`, `CANCELLED`

### Payment
- Table: `payments`
- Key fields: `id`, `booking_id`, `transaction_id`, `amount`, `status`
- Constraints: `booking_id` references `bookings.id`; `transaction_id` is unique

### BlockedSlot
- Table: `blocked_slots`
- Key fields: `id`, `court_id`, `date`, `start_time`, `end_time`, `reason`, `status`
- Constraints: `court_id` references `courts.id`

## Relationship sketch

```text
User
  ├── owns many Venue
  └── makes many Booking

Venue
  ├── has many Court
  └── has many Booking

Court
  ├── belongs to Venue
  ├── belongs to Activity
  └── may have many BlockedSlot

Activity
  └── used by Court and Booking

Booking
  ├── belongs to User
  ├── belongs to Venue
  ├── belongs to Court
  ├── belongs to Activity
  └── has one Payment
```

## Important business rules currently enforced in code

- Bookings are prevented from overlapping on the same `court_id` and booking date when a booking is `CONFIRMED`.
- SQLite booking creation uses `BEGIN IMMEDIATE` around the overlap check and inserts; the regression test against file-backed SQLite confirms only one of two concurrent same-slot submissions succeeds.
- Availability generation is only exposed for active venues and marks elapsed slots, overlapping confirmed bookings, and active blocked intervals unavailable. Cancelled bookings no longer block availability.
- Booking creation requires the venue to be `ACTIVE`.
- Booking date/time must be in the future and an exact one-hour interval within the hardcoded 06:00–23:00 schedule.
- The backend sets booking total and mock payment amount to 400; frontend amounts are not authoritative.
- Owner routes verify the owner ID from the JWT subject before acting on a venue.
- Admin routes verify `Role.ADMIN` before approving or listing protected records.

## Migration status

Tables are created at app import/startup and by the seed script with `Base.metadata.create_all()`. The repository has an Alembic directory but no `alembic.ini`, Python revision, or active migration chain; a compiled `.pyc` cache is not a usable migration. `create_all()` can create missing tables, but it does not safely evolve existing table definitions. Before future schema changes that must upgrade deployed or persistent databases, add and test a versioned migration baseline; a database migration is not needed for this stabilization because the schema was not changed.

Concurrency scope: `BEGIN IMMEDIATE` is SQLite-specific and serializes writers across the database, not only the contested court. The current local MVP is SQLite-backed and the concurrent regression passes. No cross-database concurrency guarantee or database-level interval exclusion constraint exists.

Cancellation sets `Booking.status` to `CANCELLED`. The existing payment record remains `PAID` with its `MOCK-` transaction identifier; no refund behavior is implemented or implied.

## Database status

IMPLEMENTED MODEL COUNT: 7 important tables

This is a compact local MVP schema and not a full production billing or availability platform schema.
