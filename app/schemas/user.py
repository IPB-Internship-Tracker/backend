from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.domain.user import UserRole


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    nama: str
    email: EmailStr
    role: UserRole
    created_at: datetime


class UserUpdate(BaseModel):
    """Update data dasar user (nama / email)."""
    nama: str | None = Field(default=None, min_length=2, max_length=150)
    email: EmailStr | None = None

    @field_validator("email", mode="before")
    @classmethod
    def email_to_lowercase(cls, v: str) -> str:
        """Ensure email selalu lowercase."""
        if isinstance(v, str):
            return v.lower()
        return v


class ChangePasswordRequest(BaseModel):
    password_lama: str = Field(min_length=1)
    password_baru: str = Field(min_length=8, max_length=10, description="Password 8-10 karakter: huruf, angka, atau simbol")