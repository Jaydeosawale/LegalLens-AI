-- Existing PostgreSQL installations need room for legal_professional.
-- New installations receive this schema from SQLAlchemy metadata.
ALTER TABLE users ALTER COLUMN role TYPE VARCHAR(32) USING role::text;
