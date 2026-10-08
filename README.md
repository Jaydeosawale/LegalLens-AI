# LegalLens AI

Flutter client for web, Android, and iOS with a FastAPI legal-document RAG backend.

## Current state

The app has three public workspaces: normal user, legal professional, and administrator. Existing super-admin accounts retain owner controls inside the administrator workspace.

Screens include dashboard, owned document upload/search/delete, saved research conversations, cited summaries, professional document comparison and advanced research, account preferences, user administration, research monitoring, usage analytics, AI/RAG configuration, system health, and owner-managed admin permissions. Active navigation routes no longer point to placeholder screens.

The backend uses Firebase authentication, Supabase PostgreSQL/pgvector, Groq, and Cloudflare R2. Document lists and retrieval are scoped to the owner; administrators can monitor and manage platform documents. The Android release build compiles; device verification and live-service integration must be checked for each release.

## Screen preview

The separate preview target uses sample documents and local fake API responses. It never signs into the supplied accounts or calls Groq, Firebase, Supabase, or R2. The production entry point remains `lib/main.dart`.

```bash
cd frontend
flutter run -d chrome --target tool/role_preview.dart
```

Use the role selector to review normal, legal professional, administrator, and owner views. Preview answers and health numbers are sample data.

This is an information-retrieval prototype, not legal advice. Generated answers should be checked against the cited source documents and a qualified professional before use in a legal matter.

## Local frontend

Use Flutter 3.47.2 or a compatible version. From `frontend`:

```bash
flutter pub get
flutter run -d chrome --dart-define=API_BASE_URL=http://127.0.0.1:8000
flutter analyze
flutter test
```

For an Android emulator, use `http://10.0.2.2:8000` as `API_BASE_URL`. For a physical Android or iOS device, use a reachable HTTPS API URL. The iOS target requires Xcode and signing for device distribution.

## Local backend

From `backend`, create a Python 3.11 virtual environment, install `requirements-deploy.txt`, set `EMBEDDING_BACKEND=onnx`, and configure the variables in `.env.example`. The database must support pgvector. Startup prepares application tables and upgrades older role/document-owner column types. Then run:

```bash
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

The local service-account JSON, uploaded PDFs, database files, caches, and private environment values are excluded from version control.

## Deployment

The web client runs on Vercel. The Docker backend runs on Render and connects to Supabase. Its small-instance configuration uses the same MiniLM embedding model through ONNX, uses hybrid search ranking, and leaves the optional cross-encoder disabled with `RERANK_ENABLED=false`. Scanned PDFs use Tesseract OCR in the Docker image. See [DEPLOYMENT.md](DEPLOYMENT.md) for configuration. Local document collections are not included in the repository.
