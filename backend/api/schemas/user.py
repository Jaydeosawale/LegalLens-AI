from pydantic import BaseModel, ConfigDict, EmailStr

from api.models.role import UserRole

# ---------------------------------------------------------
# Register
# ---------------------------------------------------------

class UserRegister(BaseModel):
    full_name: str
    email: EmailStr
    password: str


# ---------------------------------------------------------
# Login
# ---------------------------------------------------------

class UserLogin(BaseModel):
    email: EmailStr
    password: str


# ---------------------------------------------------------
# User Response
# ---------------------------------------------------------

class UserResponse(BaseModel):
    id: str
    full_name: str
    email: EmailStr
    role: UserRole
    is_active: bool

    model_config = ConfigDict(
        from_attributes=True
    )