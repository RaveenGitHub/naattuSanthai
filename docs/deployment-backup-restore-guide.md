# Backup, Restore, and Retention Guide

## Scope

This guide covers the SQLite database and browser session behavior for deployment and recovery. It is intended for operators performing releases, migrations, or incident recovery.

## Backup Architecture

- The live database is `digital_farming.db`.
- Backups are stored under `backups/` beside the application.
- Use `create_db_backup(label)` from `database.py` to create a timestamped SQLite copy.
- Verify available backups through `get_migration_status()` or the admin operations checklist.
- Create a backup before schema migrations, releases, and manual database changes.

PowerShell example:

```powershell
.\.venv\Scripts\python.exe -c "from database import create_db_backup; print(create_db_backup('pre-release'))"
```

## Retention Policy

- The configured policy keeps at most 10 backup files.
- Backups older than 30 days are pruned when the backup policy runs.
- Do not delete the current live database while preparing a restore.
- Copy a selected backup to a separate working location before inspecting it.

## Restore Procedure

1. Stop the application process and prevent new writes.
2. Confirm the target backup path under `backups/` and record the incident or release identifier.
3. Copy the current `digital_farming.db` to a quarantine location as evidence.
4. Restore the selected backup as `digital_farming.db`.
5. Start the application with the normal deployment command.
6. Check `/health` and `/ready` before allowing users back in.
7. Verify login, profile lookup, and one representative farmer service.

PowerShell example:

```powershell
Copy-Item .\digital_farming.db .\backups\before-restore-evidence.db
Copy-Item .\backups\pre-release-YYYYMMDD-HHMMSS.db .\digital_farming.db -Force
.\.venv\Scripts\python.exe -m uvicorn app:app --host 0.0.0.0 --port 8000
```

Never overwrite a database while the application is running.

## Session Data Management

- Sessions are represented by browser cookies containing signed access tokens.
- Cookies are HTTP-only and use `SameSite=Lax`; secure transport is enabled for HTTPS requests.
- Logout clears the session cookie.
- Session cookies are not stored in SQLite backups.
- Users must sign in again after the browser session ends, logout, token expiry, or a restored database invalidates the account state.

## Restore Verification

After a restore, run:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

At minimum, verify:

- `/health` reports a healthy database.
- `/ready` reports ready checks.
- An admin can open the quality gate.
- A farmer can open the dashboard and advisory pages.
- The restored backup contains the expected migration and backup status.

## Emergency Recovery

If the live database is corrupted or a deployment introduces incompatible data:

1. Stop writes immediately.
2. Preserve the live database and application logs.
3. Select the newest known-good backup whose health checks passed.
4. Restore using the procedure above.
5. Run health, readiness, and regression checks.
6. Record the restore time, backup name, cause, and verification results.
7. Escalate unresolved data loss or authentication issues to the release owner.

Review `docs/implementation-guide.md` and `docs/combined-roadmap.md` for release context, and use `/admin/release-runbook` for deployment rollback checks.

## Activation Email Configuration

Registration activation emails require SMTP settings in the deployment environment:

- `SMTP_HOST`: SMTP server hostname.
- `SMTP_PORT`: SMTP server port, normally `587`.
- `SMTP_USERNAME` and `SMTP_PASSWORD`: SMTP credentials when required.
- `SMTP_FROM_EMAIL`: verified sender address.
- `SMTP_USE_TLS`: `true` for STARTTLS, which is the default.

When these values are absent, the account is still created as pending verification, but no email can be delivered. Configure and test SMTP before enabling public registration.
