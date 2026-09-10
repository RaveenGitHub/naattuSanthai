# Login and registration module

## Status

Status: Implemented and validated. Authentication, verified-user gating, session handling, and protected navigation are in place for the current app baseline; remaining open items are governance and release approvals, not auth implementation gaps.

## Overview

This module allows users to create an account, verify identity, and access the app securely.

## Goals

- simple onboarding
- strong identity verification
- secure login and session handling
- rate limiting and abuse protection
- minimal personal-data exposure

## Functional requirements

- registration with email or phone
- unique username validation
- secure password policy
- OTP delivery and validation
- login allowed only for active and verified users
- lockout for repeated failed attempts
- forgot password recovery path for users who need account recovery
- registration entry point visible from the login screen for new users
- login screen must expose both recovery and account-creation actions as clear, discoverable CTAs
- forgot-password flow must include a reset request form, secure token validation, and a password reset screen
- register flow must be reachable from the login screen and must support the new user onboarding journey without requiring a deep-link workaround
- Reset Password flow: when the user clicks the Reset Password link, the system must open the Reset Password page and prompt for the registered email address
- Reset Password flow: the system must validate the email and display an appropriate error when the email is invalid or not registered
- Reset Password flow: if the email is valid and registered, the system sends a reset password link to the email
- Registration flow: when the user clicks Register User, they must be redirected to the Registration page
- Registration flow: the registration page must display the complete user registration form with all required fields
- Registration flow: the system must validate all user input values before processing submission
- Registration activation logic: if the user provides an email, the system sends an activation link to that email
- Registration activation logic: if the user provides only a phone number, the system sends an OTP to that number
- Registration activation logic: the user account remains inactive until the activation link is confirmed or the OTP is successfully verified
- Login requirement: only active and verified users are permitted to sign in to the application

## Non-functional requirements

- password hashing with a strong algorithm
- generic auth errors to avoid user enumeration
- short-lived, revocable tokens
- audit recording of auth failures and verifications
- secure handling of PII and OTP data

## Acceptance criteria

- at least one of email or phone is required
- username must be unique
- OTP expires within a short time window
- invalid credentials return a generic failure response
- unverified users cannot sign in
- inactive accounts cannot sign in until activation is completed
- active and verified users can sign in normally
- locked accounts remain blocked until reset
- login screen displays a visible Forgot password action
- login screen displays a visible Register new user action
- Reset Password flow opens the reset page from the link and prompts for a registered email
- Reset Password flow validates email and shows the correct error for invalid or unregistered email addresses
- Reset Password flow sends a reset link to valid registered email addresses
- Registration page redirects from the Register User CTA and displays the complete registration form
- Registration form validates all required fields before processing
- If an email is supplied during registration, activation is performed via email link
- If only a phone number is supplied during registration, activation is performed via OTP verification
- User accounts remain inactive until activation completes successfully
- recovery and registration actions must be accessible without requiring prior authentication
- user recovery and new-account flows must be documented as first-class product requirements rather than hidden implementation afterthoughts

## Key endpoints

- POST /api/v1/auth/register
- POST /api/v1/auth/verify-otp
- POST /api/v1/auth/login
- POST /api/v1/auth/refresh
- POST /api/v1/auth/logout
- POST /api/v1/auth/forgot-password
- POST /api/v1/auth/reset-password
- POST /api/v1/auth/verify-registration

- Enforce strong password policies.
- Store passwords using salted hashing.
- Protect OTP endpoints with rate limiting.
- Use HTTPS for all communication.
- Log authentication attempts for audit.
- Prevent enumeration attacks (generic error messages).

## 12. Authenticated Navigation & Session Control Requirements

### 12.1 Functional Requirements

- Only authenticated and verified users may access internal application pages beyond the login and registration screens.
- Users who are not authenticated must be redirected to the login page whenever they attempt to access internal routes directly.
- Direct URL access to protected pages must be blocked unless the user has a valid active session.
- The application must maintain a strict separation between public auth screens and protected app surfaces.
- If a user’s session expires or is invalidated, the next navigation attempt must route them to the login page.
- The browser session must terminate automatically when the tab or browser window is closed.
- No silent session continuation is allowed after browser shutdown or tab close.
- Session tokens must be invalidated immediately when the session ends, including browser or tab closure.
- The system must enforce session expiry and re-authentication for any stale or expired session.

### 12.2 Non-Functional Requirements

#### Security

- Use secure, short-lived session tokens with industry-standard cryptographic handling.
- Store session credentials in secure browser storage patterns only, with no background persistence.
- Enforce secure cookie or token policies, including HttpOnly, Secure, and SameSite protections as applicable.
- Prevent access via URL tampering, cached file leakage, or stale page state.
- Ensure protected routes are server-validated for authentication and verification state on each request.
- Require reauthentication for expired, invalid, or terminated sessions.

#### Performance and Reliability

- Protected route access checks must execute with minimal latency and should not degrade application responsiveness.
- Session validation must reliably fail closed when the token is missing, expired, or invalid.
- Redirect decisions for unauthenticated access must be deterministic and immediate.

#### Compliance and Operational Security

- Session handling must align with fintech-grade identity controls and secure browser practices.
- Authentication and session status must be auditable for operational review.
- Sensitive session artifacts must be excluded from logs, analytics, and client-side inspection.

### 12.3 Updated Workflow Diagrams (Text-Based)

#### Authenticated Navigation Workflow

1. User opens an internal route such as dashboard, portfolio, or goals.
2. System checks for a valid authenticated session.
3. If session is valid and user is verified → allow access.
4. If session is missing, expired, or invalid → redirect to login.
5. User is denied access to protected page content until valid authentication is completed.

#### Browser Close / Session Termination Workflow

1. User closes browser tab or browser window.
2. Session state is invalidated immediately.
3. Session token is rejected on any future request.
4. Any attempted navigation to internal pages redirects to login.
5. No silent session continuation or background authentication is allowed.

#### Session Expiry Workflow

1. User remains inactive beyond the session timeout window.
2. System marks session as expired.
3. Protected route request fails validation.
4. User is redirected to login page.
5. User must re-authenticate to regain access.

### 12.4 Updated Security Considerations

- Protected pages must not be accessible through bookmark, shared link, or direct URL manipulation without a valid authentication context.
- Cache-control and no-store protections should be applied to sensitive authenticated screens to prevent page reuse after logout or session expiry.
- Authentication state must be validated at every protected request and not only at initial page load.
- Browser session termination must invalidate any in-memory or client-side token state immediately.
- Users must never be allowed to continue a session after the browser or tab is closed.
- Any unauthorized access attempt should result in a redirect to login and a secure denial response.

### 12.5 Updated Error-Handling Scenarios

| Scenario                                                    | Error Message / Behavior                                | Required Action                |
| ----------------------------------------------------------- | ------------------------------------------------------- | ------------------------------ |
| User attempts direct access to protected page without login | Redirect to login page                                  | Require authentication         |
| Session expired                                             | Session expired; please log in again                    | Clear session and redirect     |
| Browser or tab closed and user navigates again              | Session invalid; redirect to login                      | Re-authenticate                |
| Invalid or tampered session token                           | Unauthorized access                                     | Terminate session and redirect |
| Protected page request after logout                         | Access denied; log in again                             | Force login flow               |
| Cached authenticated page is reopened                       | Page should not remain accessible without valid session | Require fresh login            |

## 13. Open Questions & Assumptions

### Open Questions

1. Should we support social login in future versions?
2. Should OTP provider be email-only or SMS-only in certain regions?
3. Should we allow passwordless login later?
4. Should session timeout be fixed at 15 minutes of inactivity or configurable by user role?

### Assumptions

- OTP provider supports global delivery.
- Username is the primary login identifier.
- Currency list is predefined and stored in system config.
- Session termination is enforced at the browser session boundary and cannot persist through browser restart.
- Authenticated application pages require verified status at every access attempt.
