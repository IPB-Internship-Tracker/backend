from pydantic import BaseModel, EmailStr, Field, field_validator

from app.domain.user import UserRole


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)

    @field_validator("email", mode="before")
    @classmethod
    def email_to_lowercase(cls, v: str) -> str:
        """Ensure email selalu lowercase."""
        if isinstance(v, str):
            return v.lower()
        return v


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: UserRole
    user_id: int


class TokenPayload(BaseModel):
    """Data yang disimpan di dalam JWT."""
    sub: str  # user_id sebagai string
    role: UserRole
    exp: int | None = None