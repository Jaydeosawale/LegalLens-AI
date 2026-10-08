from sqlalchemy.orm import Session

from api.models.role import UserRole
from api.models.user import User
from repositories.user_repository import UserRepository


class FirebaseUserService:

    # =========================================================
    # GET OR CREATE LEGALLENS USER
    # =========================================================

    @staticmethod
    def get_or_create_user(
        db: Session,
        firebase_user: dict,
    ) -> User:

        firebase_uid = firebase_user.get("uid")
        email = firebase_user.get("email")

        if not firebase_uid:
            raise ValueError(
                "Firebase token does not contain a user ID."
            )

        if not email:
            raise ValueError(
                "Firebase account does not contain an email address."
            )

        # -----------------------------------------------------
        # 1. LOOKUP BY FIREBASE UID
        # -----------------------------------------------------

        user = UserRepository.get_by_firebase_uid(
            db=db,
            firebase_uid=firebase_uid,
        )

        if user:
            return user

        # -----------------------------------------------------
        # 2. LOOKUP BY EMAIL
        #
        # Important for existing users.
        # -----------------------------------------------------

        user = UserRepository.get_by_email(
            db=db,
            email=email,
        )

        if user:

            # Link existing LegalLens account
            # with Firebase identity.
            if user.firebase_uid and user.firebase_uid != firebase_uid:
                raise ValueError("This email is linked to another Firebase account.")
            if not firebase_user.get("email_verified"):
                raise ValueError("Verify your email before linking this existing account.")
            user.firebase_uid = firebase_uid

            return UserRepository.update(
                db=db,
                user=user,
            )

        # -----------------------------------------------------
        # 3. CREATE NEW LEGALLENS USER
        # -----------------------------------------------------

        full_name = (
            firebase_user.get("name")
            or email.split("@")[0]
        )

        user = User(
            firebase_uid=firebase_uid,
            full_name=full_name,
            email=email,
            password_hash=None,
            role=UserRole.USER,
            is_active=True,
        )

        return UserRepository.create(
            db=db,
            user=user,
        )
