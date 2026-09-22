# Admin User Management Functional PRD

## 1. Product Summary

The Admin Page is a restricted-access module for administrators to view registered users, inspect profiles, and control account activation and deactivation with auditable safeguards.

## 2. Objectives

- Give administrators a reliable view of enrollment and account lifecycle state.
- Allow secure activation, deactivation, and reactivation of user accounts.
- Preserve role-based access control, data consistency, and auditability.
- Provide responsive workflows for desktop and tablet use.

## 3. Roles and Permissions

### Admin

- Access the Admin Page and user-management APIs.
- View all registered users and detailed profiles.
- Search and filter users.
- Activate, deactivate, and reactivate accounts.
- View action outcomes and audit metadata.

### System Admin (Future Extension)

- Includes all Admin permissions.
- May later manage configuration-level settings, role assignment, and audit-log administration.

### Non-admin and Guest

- Cannot access Admin Page, user-management APIs, or another user's profile.
- Direct access attempts must be rejected safely and logged where applicable.

## 4. Functional Requirements

### 4.1 Access and Security

- FR-1: Only Admin or System Admin roles may access the Admin Page.
- FR-2: Unauthenticated direct access redirects to Login; authenticated non-admin access redirects to a safe page or returns 403 for APIs.
- FR-3: Backend authorization is mandatory even when the UI hides admin navigation.
- FR-4: Every admin action records timestamp, admin identity, action type, affected user, outcome, and request context when available.

### 4.2 User List

- FR-5: Display all registered or enrolled users in a responsive table or card grid.
- FR-6: Show user ID, full name, email, phone, registration date, account status, last login date, role, and available actions.
- FR-7: Support status filters: Active, Inactive, Locked, and Pending Activation.
- FR-8: Support role filtering and search by name, email, phone, or username.
- FR-9: Support date-range filtering for registration and last-login dates.
- FR-10: Use pagination with a default page size of 25 for large datasets.

### 4.3 User Detail

- FR-11: View opens a detailed profile page or modal without exposing unrelated users' data to non-admins.
- FR-12: Details include personal and contact information, registration metadata, current status, role, last login, failed-login state, and audit-relevant lifecycle events.
- FR-13: Linked modules such as goals, portfolio, transactions, or field records are shown when those relationships exist; otherwise show an explicit empty state.

### 4.4 Account Lifecycle

- FR-14: Admin can activate Pending Activation, Inactive, or Locked users where policy permits.
- FR-15: Admin can deactivate an Active user.
- FR-16: Deactivation immediately prevents login and protected-page access.
- FR-17: Activation immediately permits login after valid credentials and verification policy.
- FR-18: Activation and deactivation require confirmation before mutation.
- FR-19: The UI shows clear success or failure feedback and preserves the current filter context.
- FR-20: The system must prevent unsafe self-lockout or require an explicit elevated confirmation policy for the final active admin.

### 4.5 Audit Logging

- FR-21: Log View, Activate, Deactivate, Reactivate, Failed Action, and Denied Action events.
- FR-22: Each event includes admin ID, affected user, action, timestamp, outcome, and optional IP/request metadata.
- FR-23: Audit records are append-only from the user-management UI.
- FR-24: Audit-log visibility is restricted to Admin initially and may be restricted to System Admin in a future role model.

### 4.6 UI and Accessibility

- FR-25: Use the same dashboard navigation and visual language as other admin pages.
- FR-26: Use clear status indicators: green Active, red Inactive/Locked, yellow Pending Activation.
- FR-27: Provide keyboard-accessible controls, visible focus states, labels, confirmation dialogs, and readable empty/error states.
- FR-28: Support desktop, tablet, and narrow mobile layouts without horizontal overflow.
- FR-29: Provide quick actions for View and the permitted lifecycle action.

## 5. Non-functional Requirements

- NFR-1: The first page of up to 10,000 users should load within 2 seconds under the agreed deployment benchmark.
- NFR-2: All mutations use authenticated API protocols and server-side authorization.
- NFR-3: Passwords, tokens, and SMTP credentials are never rendered in user-management views or logs.
- NFR-4: Account status changes are transactionally persisted and reflected consistently by login, middleware, APIs, and UI.
- NFR-5: List queries use indexed fields and bounded pagination; filtering must not require loading all records into the browser.
- NFR-6: User actions must be safe to retry without duplicate state transitions or duplicate audit events.

## 6. Acceptance Criteria

- Only an authenticated Admin or System Admin can open the Admin Page or call user-management APIs.
- Admins can list, search, filter, paginate, and inspect registered users without seeing passwords, tokens, or other secrets.
- Admins can activate, deactivate, and reactivate accounts through confirmed actions.
- Deactivation immediately blocks login and protected-page access; activation restores access according to verification policy.
- Every view, lifecycle mutation, denied request, and failed action has an audit record with actor, target, action, timestamp, and outcome.
- The UI is usable on desktop, tablet, and mobile widths with clear status indicators and accessible controls.
- The agreed performance benchmark is met for a 10,000-user dataset.

## 7. Success Metrics

- Administrators can find a user and understand their status without backend assistance.
- Valid activation/deactivation actions succeed with visible feedback.
- Unauthorized access remains blocked across direct URLs and API calls.
- Every lifecycle mutation has a corresponding audit record.
- No account-status mismatch is observed between the admin list, login, and protected-page behavior.

## 8. Future Enhancements

- Bulk activation/deactivation with batch audit records.
- CSV or Excel export with privacy review.
- Role assignment and permission management.
- Activity-monitoring dashboard and anomaly alerts.
- System Admin-only audit-log and configuration controls.
