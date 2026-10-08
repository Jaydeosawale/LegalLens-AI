import json
import os
from pathlib import Path

import firebase_admin
from firebase_admin import credentials


# =========================================================
# FIREBASE ADMIN INITIALIZATION
# =========================================================

BASE_DIR = Path(__file__).resolve().parents[3]

SERVICE_ACCOUNT_PATH = (
    BASE_DIR / "firebase-service-account.json"
)


def initialize_firebase() -> None:
    """
    Initialize Firebase Admin SDK once for the FastAPI application.
    """

    if firebase_admin._apps:
        return

    service_account_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
    if service_account_json:
        credential = credentials.Certificate(json.loads(service_account_json))
    else:
        service_account_path = Path(
            os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", str(SERVICE_ACCOUNT_PATH))
        )
        if not service_account_path.exists():
            raise FileNotFoundError(
                "Firebase service account is not configured. Set "
                "FIREBASE_SERVICE_ACCOUNT_JSON or FIREBASE_SERVICE_ACCOUNT_PATH."
            )
        credential = credentials.Certificate(str(service_account_path))

    firebase_admin.initialize_app(credential)
