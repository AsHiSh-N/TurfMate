# TurfMate Environment Skill

Maintain application configuration and environment safety.

Inspect:

* .env
* .env.example
* Docker
* docker-compose
* deployment configuration
* runtime configuration

## Rules

Never commit:

* secrets
* passwords
* API tokens
* private keys

When adding a new environment variable:

1. add to `.env.example`
2. document its purpose
3. ensure application handles missing values appropriately
4. never include the real secret

## Environment changes

Report:

* variable added
* purpose
* required/optional
* services affected

Never print secret values.
