# TurfMate Security Skill

Perform security checks for every meaningful change.

## Check

### Authentication

* protected routes
* token/session handling
* password handling

### Authorization

Verify that users cannot access resources belonging to other roles/users.

Test examples:

Customer → Owner API
Customer → Admin API
Owner → Other Owner resources

### Input

Check:

* validation
* injection
* malformed requests
* unexpected values

### Secrets

Search for:

* API keys
* passwords
* tokens
* private keys
* credentials

Never expose them.

### Booking security

Verify that a user cannot:

* manipulate another user's booking
* bypass slot availability
* alter price client-side
* book inactive venues
* access unauthorized owner data

Report security findings separately.
