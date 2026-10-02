# TurfMate Database Skill

Handle TurfMate database changes safely.

## Responsibilities

Inspect:

* schema
* models
* relationships
* migrations
* indexes
* constraints
* queries
* transactions

## Rules

For schema changes:

1. Create/update migration.
2. Update models.
3. Update affected queries/services.
4. Test migration.
5. Test existing functionality.
6. Update DATABASE.md.

## Booking-specific requirements

For booking-related changes evaluate:

* duplicate booking
* concurrent booking
* transaction boundaries
* unique constraints
* slot locking
* race conditions

Do not rely solely on frontend availability checks.

## Data integrity

Check:

* foreign keys
* nullability
* unique constraints
* indexes
* cascading behavior

Never delete or alter existing production data assumptions without explicit instruction.
