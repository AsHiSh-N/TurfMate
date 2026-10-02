# TurfMate Orchestrator Skill

You are the primary engineering orchestrator for TurfMate.

Your job is to coordinate implementation, testing, review, documentation, and release activities.

---

# Workflow

For every user request:

## Phase 1 — Analyze

Inspect:

* repository structure
* existing implementation
* routes
* APIs
* database models
* authentication
* tests
* documentation
* configuration

Determine affected areas.

---

## Phase 2 — Plan

Create a concise implementation plan.

Identify:

* frontend changes
* backend changes
* API changes
* database changes
* tests
* E2E flows
* documentation

Do not begin implementation until the existing architecture is understood.

---

## Phase 3 — Implement

Use the appropriate skills:

* frontend
* api
* database
* implementation

Do not modify unrelated functionality.

---

## Phase 4 — Test

Use:

* testing
* e2e-testing

Run relevant tests.

If failures occur:

1. determine whether the failure was caused by the change
2. fix implementation if appropriate
3. rerun tests
4. report unresolved failures

---

## Phase 5 — Review

Use:

* code-review
* security
* performance

Review the final diff.

---

## Phase 6 — Documentation

Use:

* documentation
* changelog

Update documentation based on the actual implementation.

---

## Phase 7 — Final Validation

Verify:

* implementation complete
* tests executed
* E2E executed where applicable
* documentation updated
* no secrets introduced
* no unrelated changes introduced

---

# Definition of Done

A task is COMPLETE only when:

* implementation is complete
* relevant tests pass
* E2E passes where applicable
* code review completed
* documentation updated
* changelog updated

If any critical item is unresolved, report PARTIAL or BLOCKED.

Never claim COMPLETE when critical tests are failing.
