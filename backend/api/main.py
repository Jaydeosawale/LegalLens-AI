import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.database.database import Base, engine, SessionLocal
from sqlalchemy import text
from api.database.init_platform_permissions import initialize_platform_permissions
from api.database.schema_upgrade import prepare_database

# Import models before create_all so SQLAlchemy registers all tables.
from api.models.user import User
from api.models.chat_history import ChatHistory
from api.models.conversation import Conversation
from api.models.message import Message
from api.models.feedback import Feedback
from api.models.document import Document
from api.models.document_chunk import DocumentChunk
from api.models.document_embedding import DocumentEmbedding
from api.models.admin_permission import AdminPermission
from api.models.platform_permission import PlatformPermission
from api.models.system_settings import SystemSettings, SystemEvent
from api.routers import system
from api.routers import (
    admin,
    analytics,
    auth,
    chat,
    chat_history,
    conversation,
    documents,
    feedback,
    upload,
)
from core.startup import StartupManager
from api.core.firebase import initialize_firebase

# ---------------------------------------------------------
# FastAPI App
# ---------------------------------------------------------

app = FastAPI(
    title="LegalLens AI API",
    description="Enterprise Legal RAG API",
    version="1.0.0",
)

# ---------------------------------------------------------
# Create Database Tables
# ---------------------------------------------------------

# ---------------------------------------------------------
# Startup
# ---------------------------------------------------------

@app.on_event("startup")
async def startup_event():

    with engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    prepare_database(engine, Base.metadata)
    with SessionLocal() as db:
        initialize_platform_permissions(db)

    print("=" * 80)
    print("STARTING LEGALLENS AI")
    print("=" * 80)

    print("Initializing Firebase Admin SDK...")
    initialize_firebase()
    print("Firebase Admin SDK initialized")

    StartupManager.initialize()

    print("=" * 80)
    print("LEGALLENS AI READY")
    print("=" * 80)

# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

cors_origins = [
    origin.strip().rstrip("/")
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8080").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# Routers
# ---------------------------------------------------------


print("Loading admin")
app.include_router(admin.router)
app.include_router(system.router)

print("Loading auth")
app.include_router(auth.router)

print("Loading chat")
app.include_router(chat.router)

print("Loading conversation")
app.include_router(conversation.router)

print("Loading feedback")
app.include_router(feedback.router)

print("Loading analytics")
app.include_router(analytics.router)

print("Loading documents")
app.include_router(documents.router)

print("Loading history")
app.include_router(chat_history.router)

print("Loading upload")
app.include_router(upload.router)

print("Finished loading routers")
# ---------------------------------------------------------
# Health
# ---------------------------------------------------------

@app.get("/", tags=["Health"])
def root():
    return {
        "application": "LegalLens AI",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health", tags=["Health"])
def health():
    return {
        "status": "healthy",
    }
