# TurfMate Testing Skill

Ensure every meaningful implementation change has appropriate automated tests.

## Test levels

Use the lowest appropriate level:

### Unit

Test:

* business logic
* validation
* calculations
* utility functions

### Integration

Test:

* API + database
* authentication
* service interactions
* persistence

### E2E

Test:

* real user journeys
* frontend + backend
* booking flows
* owner flows
* admin flows

## Change-based testing

Determine affected functionality from git diff.

Run:

1. directly affected tests
2. related regression tests
3. broader test suite when appropriate

## Failure handling

For failures:

* capture exact failure
* identify root cause
* fix if caused by implementation
* rerun

Never report PASS without execution.

## Final result

Report:

PASS
FAIL
BLOCKED

with test counts where available.
