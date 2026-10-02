# TurfMate Performance Skill

Review performance implications of changes.

Inspect:

* database queries
* API response time
* N+1 queries
* unnecessary frontend requests
* large payloads
* rendering
* caching
* pagination
* indexes

For booking/availability APIs pay special attention to:

* date-range queries
* slot queries
* concurrent requests
* database load

Do not optimize prematurely.

Only recommend changes supported by actual implementation or measured behavior.
