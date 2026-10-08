from enum import Enum


class UserRole(str, Enum):
    USER = "user"
    LEGAL_PROFESSIONAL = "legal_professional"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"
