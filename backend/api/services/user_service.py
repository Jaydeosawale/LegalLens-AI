from api.models.role import UserRole
from api.models.user import User
from auth.hashing import PasswordHasher
from repositories.user_repository import UserRepository


class UserService:

    @staticmethod
    def register(db, full_name, email, password):

        existing = UserRepository.get_by_email(
            db,
            email
        )

        if existing:
            raise ValueError("Email already registered.")

        user = User(
            full_name=full_name,
            email=email,
            password_hash=PasswordHasher.hash(password),
            role=UserRole.USER,
            is_active=True,
        )

        return UserRepository.create(
            db,
            user
        )

    @staticmethod
    def authenticate(db, email, password):

        user = UserRepository.get_by_email(
            db,
            email
        )

        if not user:
            return None

        if not user.is_active:
            return None

        if not PasswordHasher.verify(
            password,
            user.password_hash
        ):
            return None

        return user