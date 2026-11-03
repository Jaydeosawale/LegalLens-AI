"""Persist R2 cleanup intent in the same transaction as document deletion."""
from api.models.system_settings import SystemSettings
from api.models.document import Document

PREFIX = 'r2_cleanup:'


def queue_cleanup(db, document):
    key = document.filename
    if not key or not key.startswith('documents/'):
        return None
    identifier = PREFIX + str(document.id)
    db.add(SystemSettings(id=identifier, values={
        'object_key': key, 'owner_id': document.user_id, 'attempts': 0}))
    return identifier


def complete_cleanup(db, identifier, storage):
    task = db.get(SystemSettings, identifier)
    if task is None:
        return True
    key = task.values['object_key']
    # A replacement upload may already reference the same content-addressed key.
    if db.query(Document).filter(Document.filename == key).first() is not None:
        return False
    try:
        storage.delete_file(key)
    except Exception:
        task.values = {**task.values, 'attempts': task.values.get('attempts', 0) + 1}
        db.commit()
        return False
    db.delete(task)
    db.commit()
    return True
