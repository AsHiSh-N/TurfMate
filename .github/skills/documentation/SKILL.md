# TurfMate Documentation Skill

Maintain TurfMate documentation automatically after implementation changes.

## Documentation files

Maintain:

* docs/TURFMATE_CURRENT_IMPLEMENTATION.md
* docs/ARCHITECTURE.md
* docs/API.md
* docs/DATABASE.md
* docs/TEST_RESULTS.md
* docs/CHANGELOG.md
* docs/changes/

## Process

After implementation:

1. inspect git diff
2. identify affected areas
3. update relevant documentation
4. verify documentation against source code

## Rules

Do not regenerate unrelated documentation.

Do not document future functionality as implemented.

Mark status clearly:

IMPLEMENTED
PARTIALLY IMPLEMENTED
MOCK
KNOWN ISSUE
NOT IMPLEMENTED

## Current implementation

Update:

`TURFMATE_CURRENT_IMPLEMENTATION.md`

when user-visible functionality changes.

## Architecture

Update:

`ARCHITECTURE.md`

when system structure changes.

## API

Update:

`API.md`

when endpoints or contracts change.

## Database

Update:

`DATABASE.md`

when schema/model relationships change.

## Tests

Update:

`TEST_RESULTS.md`

with actual executed test results.

## Changes

Create/update a change record when a significant feature is implemented.
