# Deployment checklist

Publish only the clean application source. Private credentials, uploaded PDFs, database files and model caches must remain outside the repository.

## Render API

Startup widens existing role columns, converts UUID document-owner IDs to the string type used by `users.id`, and creates missing tables. API-owned tables have row-level security enabled without direct client policies: clients authenticate with Firebase through FastAPI, not through Supabase's public Data API. The backend database role must be the trusted server role.

Create a Docker web service using `render.yaml`, with root directory `backend` and Dockerfile `./Dockerfile`. The service needs Supabase PostgreSQL with pgvector, Groq API access, Firebase Admin credentials, and Cloudflare R2 credentials. Store these as Render secrets, never as committed files.

Set `CORS_ORIGINS` to the exact Vercel HTTPS origin. Set `FIREBASE_SERVICE_ACCOUNT_JSON` to the full service-account JSON as a secret, or mount a secret file and set `FIREBASE_SERVICE_ACCOUNT_PATH`. Confirm `/health`, authenticated `/auth/me`, document list/upload, and a citation-backed chat response. The current health route only proves the process is serving; it does not prove RAG dependencies are healthy.

The Docker build downloads the MiniLM ONNX model so startup can load it locally. The free-plan default disables the extra cross-encoder, retaining vector/BM25 hybrid ranking. Free instances can sleep; verify cold-start and memory behavior. Enable the cross-encoder only on an instance with sufficient memory. Do not ingest a local PDF collection by default.

## Vercel web client

Import the same repository as a Vercel project. The root `vercel.json` builds `frontend/build/web` and rewrites Flutter routes to `index.html`. Set `API_BASE_URL` to the Render HTTPS origin (without a trailing slash). The build fails if this value is absent. Add the final Vercel domain to `CORS_ORIGINS`, Firebase authorized domains, and any provider allowlists.

## Android and iOS

Build both clients with the same `API_BASE_URL` dart define. Test sign-in, document list, chat, error handling, and upload permissions on devices. Android needs a signed release build; iOS needs Xcode signing and App Store/TestFlight setup. A web deployment does not automatically publish mobile apps.

## Release gates

- Confirm Firebase service-account credentials have never been committed. Rotate any credential that was exposed.
- Verify every user's chat history and document retrieval are isolated. Users and professionals manage their own documents; administrators manage platform documents.
- Add request limits, rate limiting, and monitoring before public signup.
- Test the RAG answer against known questions and ensure citations point to the right document and page.
- Verify uploaded documents are licensed for this use and that the UI states this is not legal advice.
- Review the GitHub diff and production configuration before enabling automatic deployment.
