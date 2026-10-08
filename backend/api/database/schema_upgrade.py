from sqlalchemy import inspect, text


def prepare_database(engine, metadata):
    """Upgrade existing IDs and deny direct client access to API-owned tables."""
    with engine.begin() as connection:
        if connection.dialect.name == "postgresql":
            inspector = inspect(connection)
            if inspector.has_table("users"):
                connection.execute(text(
                    "ALTER TABLE users ALTER COLUMN role TYPE VARCHAR(32) USING role::text"
                ))
            if inspector.has_table("documents"):
                for definition in (
                    "approval_status VARCHAR(20) NOT NULL DEFAULT 'draft'",
                    "submitted_by VARCHAR(36)",
                    "rag_scope VARCHAR(20) NOT NULL DEFAULT 'private'",
                    "access_enabled BOOLEAN NOT NULL DEFAULT true",
                    "reviewed_by VARCHAR(36)",
                    "reviewed_at TIMESTAMPTZ",
                    "review_note TEXT",
                ):
                    connection.execute(text(f"ALTER TABLE documents ADD COLUMN IF NOT EXISTS {definition}"))
                columns = {column["name"]: column for column in inspector.get_columns("documents")}
                if str(columns["user_id"]["type"]).lower() == "uuid":
                    connection.execute(text(
                        "ALTER TABLE documents ALTER COLUMN user_id TYPE VARCHAR(36) USING user_id::text"
                    ))
        metadata.create_all(connection)
        if connection.dialect.name == "postgresql":
            # Firebase tokens are verified by FastAPI. Supabase public clients
            # must not bypass that API to access users or document content.
            quote = connection.dialect.identifier_preparer.quote
            for table in metadata.sorted_tables:
                connection.execute(text(
                    f"ALTER TABLE {quote(table.name)} ENABLE ROW LEVEL SECURITY"
                ))
