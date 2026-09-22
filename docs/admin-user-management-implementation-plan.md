# Admin User Management Implementation Plan

## 1. Scope and Delivery Strategy

Implement the Admin Page as a server-authorized user-management module. Deliver the read-only list and detail workflow first, then lifecycle mutations, audit coverage, and performance hardening. Preserve the existing Admin role and treat System Admin as a future extension until a separate role is introduced.

## 2. Current Repository Baseline

- Admin HTML pages and API routes already require admin authorization.
- User records already contain profile, role, status, registration, login, and failed-login fields.
- Audit-log storage and admin audit views already exist.
- Existing unlock behavior can be reused as the first activation capability.
- The current user list API is minimal and must be expanded for the PRD fields and filters.

## 3. Phase 1 - Data Contract and Authorization

### Tasks

- Define typed response schemas for user summaries, user details, filters, paginated results, and lifecycle mutations.
- Define canonical statuses: `active`, `inactive`, `locked`, and `pending_verification` with farmer-facing labels.
- Add server-side admin authorization to every user-management API and page route.
- Add explicit self-access and affected-user checks for detail and mutation operations.
- Confirm deactivated or locked accounts cannot authenticate or use protected pages.
- Define an audit event contract containing admin ID, affected user, action, outcome, timestamp, and optional IP.

### Acceptance

- Non-admin and unauthenticated callers are rejected safely.
- Admin callers receive consistent status and error responses.
- Status transitions are enforced by the backend, not only by UI controls.

## 4. Phase 2 - User List API and Admin UI

### Tasks

- Extend the user list query to return user ID, name, email, phone, role, status, created date, and last login.
- Add search across username, full name, email, and phone.
- Add role, status, and registration/last-login date filters.
- Add bounded pagination with default size 25 and maximum size 100.
- Add indexes for status, role, created date, last login, email, and phone where SQLite usage supports them.
- Build the Admin Page table and responsive card fallback using the existing dashboard navigation.
- Add loading, empty, error, and no-results states.
- Add accessible status badges and keyboard-safe action controls.

### Acceptance

- Admin can find a user by name, email, phone, or username.
- Pagination and filters preserve query state.
- The page remains usable on desktop, tablet, and mobile widths.

## 5. Phase 3 - User Detail View

### Tasks

- Add `GET /api/admin/users/{username}` or an equivalent ID-based detail endpoint.
- Render personal, contact, registration, role, status, last-login, and failed-login information.
- Render linked module summaries when available and explicit empty states otherwise.
- Record an audit event for sensitive profile views.
- Ensure detail routes never allow non-admin cross-user access.

### Acceptance

- Admin can open a complete profile without exposing passwords, tokens, or secrets.
- Detail data matches the list record and database state.
- View events are auditable.

## 6. Phase 4 - Activation and Deactivation

### Tasks

- Add a single transition endpoint with an allowlisted action: activate, deactivate, or reactivate.
- Reuse existing unlock semantics where appropriate and add inactive/deactivated state handling.
- Reject invalid transitions, unknown users, and unsafe final-admin lockout.
- Add confirmation dialogs for all UI mutations.
- Show success/failure feedback without losing current filters or page position.
- Immediately enforce status in login, token/session validation, middleware, and protected APIs.
- Record success and failure audit events for every attempted mutation.

### Acceptance

- Pending or inactive users can be activated by an admin.
- Active users can be deactivated and immediately lose access.
- Reactivation restores access after valid login and policy checks.
- Repeated requests are safe and do not create inconsistent status or duplicate transitions.

## 7. Phase 5 - Audit and Operational Monitoring

### Tasks

- Add admin user-management actions to the audit-log filter and detail view.
- Add affected-user and action filters for lifecycle investigations.
- Include denial and failed-action events with safe diagnostic details.
- Add operational metrics for action counts, failures, and average list-query latency.
- Ensure audit data is retained according to the deployment policy and excluded from secret output.

### Acceptance

- Every View, Activate, Deactivate, Reactivate, and denied action can be traced.
- An administrator can reconstruct who changed an account and when.
- Monitoring identifies repeated failures or unusual lifecycle activity.

## 8. Phase 6 - Testing and Release Readiness

### API Tests

- Admin can list users and receive pagination metadata.
- Search, role, status, and date filters return only matching records.
- Admin can view a complete user detail response.
- Non-admin, guest, invalid-token, and cross-user requests are rejected.
- Activation, deactivation, and reactivation persist correct status.
- Deactivated users cannot log in or access protected pages.
- Every lifecycle action creates the expected audit event.

### UI Tests

- Admin table renders all required columns and status indicators.
- Empty, error, filtered, and paginated states render correctly.
- Confirmation dialog appears before mutation.
- Success and failure messages are visible and accessible.
- Mobile/tablet layouts do not overflow horizontally.

### Performance and Security Tests

- Benchmark first-page list load with a representative 10,000-user dataset.
- Verify bounded SQL pagination and indexed filters.
- Confirm password hashes, tokens, SMTP credentials, and sensitive audit details never appear in HTML or JSON responses.
- Run the complete regression suite before release.

## 9. Suggested File Changes

- `app.py`: admin page routes, HTML rendering, and request wiring.
- `security.py`: status transitions, user detail queries, and audit-safe lifecycle operations.
- `schemas_auth.py` or a new admin schema module: request/response validation.
- `database.py`: indexes or migrations for list filters and pagination.
- `tests/test_api.py`: API authorization, lifecycle, and audit tests.
- `tests/test_auth_ai.py`: browser workflow and responsive content checks.
- `docs/admin-user-management-prd.md`: product contract.

## 10. Delivery Order

1. Define statuses, schemas, authorization, and audit contract.
2. Expand paginated list API and implement the responsive list UI.
3. Add detail view and profile-view audit events.
4. Add activation/deactivation/reactivation with immediate access enforcement.
5. Add audit filters and operational metrics.
6. Run security, performance, accessibility, and full regression validation.

## 11. Definition of Done

- Admin-only access is enforced on every page and API path.
- User list supports required fields, filters, search, and pagination.
- User detail view is complete and secret-safe.
- Account lifecycle actions are confirmed, persisted, immediately enforced, and audited.
- Responsive UI and error states are tested.
- Release documentation, rollback guidance, and exact verification commands are recorded.
