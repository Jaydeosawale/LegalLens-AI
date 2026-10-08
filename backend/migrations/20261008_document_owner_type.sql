-- Align document owners with users.id without deleting documents.
BEGIN;
ALTER TABLE documents ALTER COLUMN user_id TYPE VARCHAR(36) USING user_id::text;
COMMIT;
