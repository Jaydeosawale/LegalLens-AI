# LegalLens Play release operations

Release source follows published main b65e8d5, which is newer than the uncommitted legacy Downloads copy. That original copy is preserved.

## Content reports

The app submits the selected AI answer, chosen reason and optional details to authenticated `POST /content-reports`. Reports are persisted in a dedicated table, limited to 20 per account per day. Authorized administrators review the latest 100 reports using `GET /content-reports` and mark them reviewed/resolved/dismissed with `PATCH /content-reports/{id}`. Check pending reports regularly, investigate against cited sources, and correct unsafe prompts/content. Do not copy report text into unrelated services. Database startup creates this table and enables the same row-level protection as other API-owned tables.

## Verified account deletion requests

Support: jaydeep.sawale97@gmail.com. Verify control of the registered email, never request passwords or identity documents. Complete within 30 days. Locate the Firebase UID and corresponding internal user ID. Delete owned R2 objects using the storage service, document embeddings/chunks and document records. Review any separately approved shared-library submission for removal. Delete conversation messages and conversations, chat feedback/history, content reports, daily chat usage, per-user system-settings/preferences and account metadata; remove Firebase authentication identity. Remove or redact user identifiers from operational events unless security or legal retention applies. Use a transaction for database records, verify counts and storage removal, then confirm completion. Restricted provider backups expire on their normal cycles. This runbook does not automatically delete any user data.

## Signing

Release upload key and key.properties are private local files, excluded from Git. Preserve both securely; do not use the old debug certificate for Play uploads. Target SDK 36. Package remains the Firebase-registered `com.jaydeo.legallens.frontend_flutter`.
