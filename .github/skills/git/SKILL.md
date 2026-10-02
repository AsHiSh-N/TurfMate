# TurfMate Git Skill

Maintain clean and auditable changes.

## Before implementation

Inspect:

* git status
* current branch
* uncommitted changes

Do not overwrite unrelated user changes.

## After implementation

Inspect:

`git diff`

Check:

* expected files only
* no secrets
* no generated junk
* no debug code
* no accidental configuration changes

## Commit guidance

When requested to commit, create focused commits.

Prefer:

feature
→ tests
→ documentation

or one coherent commit when appropriate.

Never force-reset user work without explicit instruction.
