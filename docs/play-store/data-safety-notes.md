# Data Safety review

Firebase email/password authentication; name, email, user identifier required for account access. No implemented OAuth option. Firebase/service request identifiers conservatively disclosed for authentication and security. No advertising or analytics SDK is configured in app source. Unused secure-storage plugin removed; Firebase manages authentication state.

Questions, answers, history, search queries, preferences, PDF files and extracted content, and user reports are stored or processed by FastAPI/PostgreSQL/Supabase, R2, Render and Groq. User-initiated research/file/report types are optional; technical diagnostics/interactions and account identifiers required. AI-bound prompts, document excerpts and user context are conservatively marked shared for functionality, without assuming all third-party processing qualifies for a service-provider exemption. No model-training or zero-retention guarantee is claimed. Groq's data-handling page governs provider retention.

No location, contacts, SMS inbox, camera/microphone, financial account integrations, billing or advertising identifiers requested. PDF file chooser grants selected-file access; no broad storage permission. Arbitrary sensitive content should not be uploaded; file/doc and user-content disclosures cover the document workflow.

HTTPS only and backup disabled on Android. Public account and selected-data deletion requests via support email; see operations.md for actual removal steps and retention exceptions. No automated deletion endpoint is claimed.

Review the imported Console preview before saving. The 11 selected data types include personal info, in-app messages, files/docs, app activity, diagnostics and service identifiers. No independent security review/UPI badge claimed.
