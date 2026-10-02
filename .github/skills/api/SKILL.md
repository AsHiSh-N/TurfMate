# TurfMate API Skill

Maintain consistent and secure APIs.

## Before changing an API

Inspect:

* existing endpoint
* request schema
* response schema
* authentication
* authorization
* validation
* error handling
* frontend consumers

## API standards

Every endpoint should have:

* clear HTTP method
* validation
* authentication where required
* authorization
* predictable response
* meaningful errors
* appropriate status codes

## Changes

When an API changes:

1. Update implementation.
2. Update tests.
3. Update API documentation.
4. Check all frontend consumers.
5. Run regression tests.

Do not silently break existing API consumers.

## Documentation

Update:

`docs/API.md`

Include:

* method
* endpoint
* authentication
* authorization
* request
* response
* errors
