from sqlalchemy.orm import Session

from api.models.user import User


class UserRepository:

    # =========================================================
    # GET BY EMAIL
    # =========================================================

    @staticmethod
    def get_by_email(
        db: Session,
        email: str,
    ):
        return (
            db.query(User)
            .filter(User.email == email)
            .first()
        )

    # =========================================================
    # GET BY INTERNAL ID
    # =========================================================

    @staticmethod
    def get_by_id(
        db: Session,
        user_id: str,
    ):
        return (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

    # =========================================================
    # GET BY FIREBASE UID
    # =========================================================

    @staticmethod
    def get_by_firebase_uid(
        db: Session,
        firebase_uid: str,
    ):
        return (
            db.query(User)
            .filter(User.firebase_uid == firebase_uid)
            .first()
        )

    # =========================================================
    # CREATE USER
    # =========================================================

    @staticmethod
    def create(
        db: Session,
        user: User,
    ):
        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    # =========================================================
    # UPDATE USER
    # =========================================================

    @staticmethod
    def update(
        db: Session,
        user: User,
    ):
        db.commit()
        db.refresh(user)

        return user
