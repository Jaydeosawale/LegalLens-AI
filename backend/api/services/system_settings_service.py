import os
from api.database.database import SessionLocal
from api.models.system_settings import SystemSettings


def get_system_settings(db=None):
    defaults = {"model_name": os.getenv("MODEL_NAME", "openai/gpt-oss-120b"), "temperature": 0.0, "top_k": 8}
    if db is not None:
        record = db.get(SystemSettings, "default")
        return {**defaults, **(record.values if record else {})}
    with SessionLocal() as session:
        return get_system_settings(session)
