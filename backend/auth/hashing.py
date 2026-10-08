from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


class PasswordHasher:

    @staticmethod
    def hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify(password: str, hashed_password: str) -> bool:
        return pwd_context.verify(
            password,
            hashed_password
        )