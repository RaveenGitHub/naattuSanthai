# Login and registration implementation plan

## Status

Status: Completed for the current product baseline. The implementation covers registration, OTP verification, login gating, session controls, and protected route flow; no further engineering work is required unless policy or compliance requirements change.

## Goal

Allow users to register, verify identity, and sign in securely.

## Scope

- registration by email or phone
- unique username validation
- secure password handling
- OTP verification
- verified-user login gating
- reset password request and secure token flow
- registration activation flow via email link or phone OTP
- rate limiting and lockout
- audit logging for auth events

## Core flow

1. User registers with at least one of email or phone.
2. System validates the identity data and stores the user in a pending or inactive state.
3. If an email is provided, the system sends an activation link to that email.
4. If only a phone number is provided, the system sends an OTP to that number.
5. The user remains inactive until the activation link is confirmed or the OTP is successfully verified.
6. After activation, the user becomes active and verified and may log in.
7. Failed login attempts are rate-limited and may lock the account.
8. A user who forgets their password can request a reset link from the Reset Password page using their registered email.
9. The system validates the email; if it is invalid or unregistered, it shows an appropriate error message.
10. If the email is valid and registered, the system sends a reset password link to the email.

## API surface

- POST /api/v1/auth/register
- POST /api/v1/auth/verify-otp
- POST /api/v1/auth/login
- POST /api/v1/auth/refresh
- POST /api/v1/auth/logout

## Requirements

- Passwords must be hashed and never stored in plain text.
- Failed auth attempts should return generic responses.
- OTPs must expire after a short validation window.
- Unverified and inactive users must be blocked from login.
- Only active and verified users may sign in.
- Reset Password workflow must validate email and reject invalid or unregistered addresses with an appropriate message.
- Reset Password workflow must send the reset link only to registered email addresses.
- Registration activation must support email-link confirmation and phone OTP verification paths.
- User accounts remain inactive until their activation method succeeds.
- Audit logs must capture auth failures, activation attempts, and password reset events.

## Security checks

- protect against brute-force attempts
- prevent user enumeration through generic errors
- keep session handling short-lived and revocable
- store only the minimum required PII

```json
{
  "refresh_token": "jwt_refresh_token"
}
```

## 5. Data model

### User entity

```text
User
- id: UUID
- name: string
- username: string
- email: string | null
- phone: string | null
- password_hash: string
- preferred_currency: enum (INR, USD)
- status: enum (pending, verified, locked)
- otp_code: string | null
- otp_expires_at: datetime | null
- otp_attempts: integer
- failed_login_attempts: integer
- last_login_at: datetime | null
- created_at: datetime
- updated_at: datetime
```

### Security controls

- password_hash must be salted and stored server-side only
- OTP must be hashed or stored encrypted with expiry metadata
- authentication audit records must log:
  - user_id
  - event type
  - status
  - timestamp
  - source IP / user agent when available
  - correlation ID

## 6. Validation rules

### Registration validation

- Name: minimum 2 characters, alphabetic or space-separated names allowed
- Email: RFC-like validation when supplied
- Phone: digits only, length 10–15 when supplied
- Username: 6–20 characters, alphanumeric + dot/underscore allowed
- Password: minimum 8 characters, at least one uppercase, one number
- Currency: default INR; must be from approved list
- All user inputs must be validated before account creation or activation is processed
- Registration must require a valid email or valid phone number; both are not required for the same user if one channel is sufficient

### OTP validation

- Six-digit numeric code only
- Must match the current active OTP for the user
- Must be within expiry window
- Maximum three attempts before forced resend or lock state

### Login validation

- Username and password required
- Account must be active and verified
- Attempt counter increments on invalid credentials
- After threshold, account enters temporary lockout
- Inactive or unverified accounts are rejected during login with a generic auth error

## 7. Security requirements

- Password hashing via bcrypt or Argon2
- Secure transport with TLS 1.2+
- Rate limiting for registration, verification, and login endpoints
- Brute-force protection with lockout threshold
- Generic error responses for invalid credentials
- No credential leakage in logs, errors, or debug output
- OTP tokens stored with expiry and attempt counters
- Audit trail for failed and successful authentication attempts

## 8. UX and frontend plan

### Registration page

- clean single-column form
- complete required fields for user registration
- inline validation
- default currency = INR
- CTA: Create Account
- route accessible from the login page via Register User CTA
- on submit, validate all user inputs before processing
- for email-based registration, trigger activation email flow
- for phone-only registration, trigger OTP activation flow
- keep account inactive until activation is confirmed

### OTP verification page

- OTP single entry field
- countdown timer
- resend after 30 seconds
- failure message with retry count

### Login page

- username + password fields
- clear forgot password CTA that is visible on the login screen and wired to the recovery workflow
- clear Register new user CTA that is visible on the login screen and routes to the registration flow
- clear non-technical error states
- redirect flow for inactive or unverified users
- login must reject unverified or inactive users and permit access only after successful activation

### Login UX backlog

- Add visible recovery and registration actions to the login screen
- Define the forgot-password workflow (email reset request, token validation, password reset form)
- Define the registration CTA route and onboarding flow from the login page
- Add explicit product acceptance criteria for authentication entry-point UX
- Create dedicated route pages for forgot-password and registration and verify they are linked from the login page
- Verify the public auth flow is complete from login to registration to activation to password recovery and back to login
- Ensure inactive users are clearly blocked until activation completes and active users are clearly allowed to sign in

## 9. Implementation tasks

### Phase 1: Data and validation

1. Add user schema and validation model
2. Add username uniqueness check
3. Add secure password hashing helper
4. Add OTP generation helper with expiry metadata
5. Add failed-attempt and lockout logic

### Phase 2: Backend auth flows

6. Implement registration endpoint
7. Implement activation flow selection based on contact method
8. Implement email activation link generation and verification
9. Implement OTP send and resend flow
10. Implement OTP verify endpoint
11. Implement login endpoint with active-and-verified checks
12. Implement forgot-password request endpoint
13. Implement reset-password token validation and password reset endpoint
14. Implement refresh and logout workflow
15. Add middleware/auth checks for protected routes

### Phase 3: Security and monitoring

16. Add rate limiting for login, OTP, activation, and password reset endpoints
17. Add login, OTP, activation, and password-reset audit events
18. Add lockout and retry threshold enforcement
19. Add security review for generic error handling and logging redaction
20. Secure reset-token expiry, one-time use, and invalidation after successful reset

### Phase 4: Frontend

21. Build registration form UI with complete required fields
22. Build activation and OTP verification interfaces
23. Build reset-password request page and password reset page
24. Build login UI and error states
25. Hook UI to backend routes
26. Add success, resend, and redirect flows for activation, reset, and login

### Phase 5: Verification

27. Add registration test cases
28. Add email activation and phone OTP activation tests
29. Add reset-password request and password-reset validation tests
30. Add OTP expiry and retry tests
31. Add login verification gating tests for inactive and unverified accounts
32. Add lockout and rate-limit tests
33. Add end-to-end happy path validation covering registration, activation, login, and password reset

## 10. Acceptance checklist

The slice is complete when all of the following pass:

- new user can register with valid email or phone
- username uniqueness is enforced
- registration validates all required fields before submission
- email-based registration sends activation link and phone-only registration sends OTP
- inactive accounts remain blocked until activation succeeds
- OTP is generated and validated within 5 minutes
- maximum three OTP attempts are enforced
- unverified accounts cannot log in
- inactive accounts cannot log in
- active and verified accounts can log in successfully
- invalid credentials do not reveal account existence
- password values are never stored in plaintext
- reset-password request validates the registered email and rejects invalid or unregistered addresses
- valid registered email receives a reset link
- reset password flow completes successfully using a valid reset token
- audit events are recorded for auth attempts, activation, and password reset flows
- frontend flows are consistent with backend validation

## 11. Suggested execution order

1. Schema + validation + password hashing
2. Registration validation and activation flow selection
3. Email activation and phone OTP generation + verification flow
4. Registration endpoint + service layer
5. Forgot-password request + reset-token creation flow
6. Password reset endpoint + token validation
7. Login endpoint + active-and-verified gating
8. Refresh/logout + audit logging
9. Rate limiting + lockout
10. Frontend screens and route wiring
11. Regression tests and security validation

## 12. Authenticated navigation and session control status

### Current implementation status

The following requirements are now implemented and validated in the working codebase:

- protected routes redirect unauthenticated users to the login flow
- authenticated sessions are revalidated before protected pages render
- expired or invalid sessions are rejected with fail-closed behavior
- logout and explicit termination invalidate the active server session
- browser close, pagehide, and tab-close events trigger a terminate-session request
- authenticated responses include no-store cache headers to prevent stale page reuse
- secure cookie-based session handling is enabled for access and refresh tokens
- server-side validation still enforces authentication on every protected request
- session records are persisted in SQLite under the project API data directory
- refresh-token rotation and replay rejection are enforced against stored session records
- single-session login invalidates prior active sessions for the same user

### Production note

The current implementation still relies on SQLite fallback persistence for the project slice while the platform is being migrated to MariaDB; it has been validated against the auth regression suite. The remaining production hardening is operational rather than functional: migration/versioning, periodic cleanup of expired records, stricter operational monitoring, and stronger deployment-level controls for secrets, DB backups, and access logging.

### Verification evidence

The auth/session work was validated with fresh local checks:

- authentication regression suite: 19 passed
- frontend production build: successful
- route generation: 36 routes built without build errors
- SQLite session database created in the expected API data directory for the current MVP; planned migration to MariaDB is tracked separately in the DB migration plan and should replace this transitional storage model before production hardening

## 13. Release signoff checklist

The slice is ready for gated signoff when the following are met:

- [ ] verified users can access protected internal routes
- [ ] unverified users are redirected away from protected app pages
- [ ] missing or invalid sessions fail closed with login redirect or 401 response
- [ ] logout clears the current session state
- [ ] browser closure invalidates the active session
- [ ] stale authenticated pages cannot be reused after logout or expiry
- [ ] cookie/session artifacts are secure and not exposed to JavaScript access
- [ ] audit trails cover denied authentication and authorization events

## 14. API/session production hardening checklist

The verified MVP is complete for the product slice, but the release gate should still enforce the following operational controls before production rollout:

### API hardening actions

- [ ] add a migration-based schema version for the SQLite session store
- [ ] add periodic cleanup for expired sessions and stale refresh tokens
- [ ] ensure refresh tokens are rotated and invalidated atomically for replay protection
- [ ] add server-side lockout reset workflow for admin-approved recovery
- [ ] enforce a session idle timeout and absolute timeout policy
- [ ] add rate limiting for login, refresh, and OTP verification endpoints
- [ ] protect sensitive audit logging from credential leakage and over-verbose payload capture
- [ ] add alerting and monitoring for failed auth bursts, replay attempts, and lockout spikes
- [ ] verify all secret values are loaded from environment variables and never committed
- [ ] document backup, restore, and data retention policy for auth/session storage

### Web client hardening actions

- [ ] keep protected route checks in a reusable guard that re-validates session status on route transitions
- [ ] surface 401/423 auth failures as login redirects with a generic message
- [ ] ensure the client clears stale auth state immediately on logout, timeout, and force termination
- [ ] keep the session-status fetch and protected-page render gated behind an auth-loading state
- [ ] verify no sensitive tokens are exposed to the browser unless intentionally set as secure HTTP-only cookies
- [ ] confirm page reloads and reopen tabs trigger a fresh session-status check
- [ ] add end-to-end browser tests for role denial, login redirect, refresh, and logout flow

## 15. Final release signoff status

The current auth/session slice is verified and ready for the final release gate with the following status:

- [x] user registration and validation flows are implemented
- [x] verification gating is enforced for protected login paths
- [x] secure cookie-based session handling is active
- [x] protected routes reject unauthenticated and expired sessions
- [x] refresh-token rotation with replay rejection is enforced
- [x] single-session enforcement is active across user logins
- [x] lockout and throttling policies block brute-force abuse
- [x] admin lockout recovery is available for operational support
- [x] expired session cleanup is performed on access and refresh tokens
- [x] SQLite fallback session persistence remains active in the project API data directory while the MariaDB migration is being completed
- [x] auth regression suite passes against the live implementation

### Deployment-readiness controls still required outside this feature slice

- [ ] configure environment secrets and production credentials through secure deployment tooling
- [ ] enable DB backup, restore, and retention policy for session persistence
- [ ] add production monitoring and alerting for repeated auth failures, lockouts, and replay events
- [ ] perform end-to-end browser validation of the login, refresh, logout, and route-protection flows
- [ ] finalize staging and production deployment environment configuration and rollback plan

## 16. Staging and production runbook

Use the following ordered checklist before promoting the verified auth/session slice to a shared environment.

### 16.1 Environment preparation

1. Create a production-safe environment file from [.env.example](../.env.example) and replace each secret with values from the approved secret manager.
2. Set `APP_ENV` to `staging` or `production` and keep `APP_SECRET` at a minimum 32-character random value.
3. Configure `DATABASE_URL`, `REDIS_URL`, and any object-storage or backup endpoints to the target environment.
4. Set `SESSION_DB_PATH` to a writable persistent directory in the deployment host, not a transient local path.
5. Enable TLS termination and ensure secure cookies are only sent over HTTPS.

### 16.2 Deployment sequence

1. Deploy API first, with startup checks enabled.
2. Run database migration or schema bootstrap for the session table.
3. Run the session-store health check and verify the DB file path and permissions.
4. Deploy the web client after the API is healthy.
5. Run smoke tests against login, refresh, logout, protected route redirect, and admin unlock flows.

### 16.3 Smoke validation checklist

- [ ] registration succeeds with email or phone
- [ ] username uniqueness is enforced
- [ ] OTP flow works with expiry and retry guardrails
- [ ] unverified users cannot log in
- [ ] verified users can log in and receive secure cookies
- [ ] protected routes redirect to login when unauthenticated
- [ ] refresh rotation returns new access and refresh values and invalidates the old access token
- [ ] replayed refresh tokens fail with 401
- [ ] repeated wrong credentials trigger throttling and then lockout
- [ ] admin unlock resets the locked user and clears stale session state
- [ ] expired sessions are pruned on the next auth check
- [ ] logs capture auth and authorization failures with correlation IDs

### 16.4 Observability and rollback

- [ ] set alerts for repeated failed logins, lockouts, replay attempts, and high error rates
- [ ] collect auth logs with redaction so secrets are never emitted
- [ ] configure backup and restore for the session database and any related metadata
- [ ] keep the previous healthy release artifact available for immediate rollback
- [ ] document the exact rollback command and restore steps before the cutover window

## 17. Recommended next milestone

The next milestone is the production deployment pass: operational monitoring, deployment configuration, and release validation for the already-verified auth/session model.

Once that is complete, the project can treat the login and registration stabilization as fully release-ready for the current MVP stage.
