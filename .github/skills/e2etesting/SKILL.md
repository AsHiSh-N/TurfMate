# TurfMate E2E Testing Skill

Validate TurfMate through real user journeys.

## Primary flows

### Customer

* open application
* search city
* filter sport
* select venue
* view availability
* select court
* select date
* select slot
* create booking
* verify confirmation
* view booking
* cancel where supported

### Owner

* login
* open dashboard
* manage venue
* manage court
* manage slots
* view bookings

### Admin

* login
* access admin dashboard
* manage users
* manage venues
* inspect bookings

Only test flows that actually exist.

## After every relevant change

Determine whether the change affects an E2E journey.

If yes, run the affected journey.

## Evidence

Record:

* test name
* result
* duration where available
* failure point
* error
* screenshot/video if test framework supports it

## Critical rule

Never call an E2E test PASS if it was not executed.
