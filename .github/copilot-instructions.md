# TurfMate — Engineering Instructions

## Project

TurfMate is a sports venue marketplace for discovering sports venues, checking court/slot availability, and booking sports facilities.

The system supports customers, venue owners, and administrators.

---

# Core Engineering Rule

Every requested change must follow this lifecycle:

ANALYZE
→ PLAN
→ IMPLEMENT
→ TEST
→ REVIEW
→ DOCUMENT
→ REPORT

A feature is NOT considered complete merely because the code has been written.

---

# Mandatory Engineering Standards

For every change:

1. Inspect the existing implementation before modifying code.
2. Understand affected frontend, backend, API, database, authentication, and configuration.
3. Reuse existing architecture and patterns.
4. Avoid unnecessary rewrites.
5. Implement the smallest clean change that satisfies the requirement.
6. Add or update automated tests.
7. Run relevant tests.
8. Run affected E2E flows where applicable.
9. Perform a security/code-quality review.
10. Update documentation.
11. Update CHANGELOG.md.
12. Report exactly what was changed and tested.

---

# Source of Truth

The actual codebase is the source of truth.

Never document or claim functionality that does not exist.

If functionality is incomplete, explicitly mark it as:

* IMPLEMENTED
* PARTIALLY IMPLEMENTED
* MOCK / PLACEHOLDER
* KNOWN ISSUE
* NOT IMPLEMENTED

Never convert planned functionality into documented implemented functionality.

---

# Skill System

Use the appropriate skills from `.github/skills/`.

Primary orchestration:

`orchestrator`

Supporting skills:

* implementation
* database
* api
* frontend
* testing
* e2e-testing
* code-review
* security
* performance
* documentation
* changelog
* environment
* git
* release

The orchestrator determines which skills are required for each request.

---

# Testing Rule

Never claim that a test passed unless it was actually executed.

Never claim an E2E flow passed unless it was actually executed.

If a test cannot be executed because of an environment problem, report:

`BLOCKED — TEST NOT EXECUTED`

Do not convert a blocked test into PASS.

---

# Documentation Rule

After every meaningful implementation change, inspect the git diff and update only the documentation affected by the change.

Possible documentation:

* docs/TURFMATE_CURRENT_IMPLEMENTATION.md
* docs/ARCHITECTURE.md
* docs/API.md
* docs/DATABASE.md
* docs/TEST_RESULTS.md
* docs/CHANGELOG.md
* docs/changes/

---

# Security Rules

Never:

* expose secrets
* commit API keys
* expose passwords
* hardcode credentials
* disable authentication to make tests pass
* bypass authorization
* weaken security controls without explicit approval

If a secret is discovered, redact it.

---

# Database Rules

Database schema changes must be handled through the project's migration mechanism.

Never silently modify schema expectations without updating migrations and documentation.

Consider:

* existing data
* backward compatibility
* indexes
* constraints
* rollback
* concurrent access

---

# Booking Rules

Booking is a critical business flow.

Changes involving:

* availability
* slots
* bookings
* cancellations
* pricing
* payments

must consider concurrency and duplicate booking scenarios.

Never assume checking availability on the frontend is sufficient.

Server-side validation must enforce booking rules.

---

# Final Response

Every completed task must report:

## Changed

What was implemented.

## Files Changed

Important files modified.

## Tests

Tests actually executed and their results.

## E2E

Relevant E2E flows executed and their results.

## Documentation

Documentation updated.

## Security Review

Important security checks performed.

## Known Issues

Remaining issues, limitations, or blocked tests.

## Status

One of:

* COMPLETE
* PARTIAL
* BLOCKED

Do not hide failures.
